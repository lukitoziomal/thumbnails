from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied, ValidationError

import random
import string
from datetime import datetime
import pytz

from .models import Image, Thumbnail, TemporaryLink
from .serializers import ImageSerializer


class UserImagesView(viewsets.ModelViewSet):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Image.objects.filter(owner=self.request.user)

    def list(self, request):
        # delete expired links
        now = pytz.utc.localize(datetime.utcnow())
        tmp_links_qs = TemporaryLink.objects.filter(
            valid_to__lt=now
        )
        for tmp_link in tmp_links_qs:
            tmp_link.delete()

        fields = ['owner', 'original_file', 'temp_link', 'thumbnails']
        queryset = self.get_queryset()
        if not request.user.is_staff:
            if not request.user.account_tier.original_link:
                fields.remove('original_file')
            if not request.user.account_tier.generate_links:
                fields.remove('temp_link')
        serializer = ImageSerializer(
            queryset,
            many=True,
            fields=fields,
            context={'request': request}
        )
        return Response(serializer.data)

    def create(self, request):
        if request.data['original_file']:
            image = Image.objects.create(
                owner=request.user,
                original_file=request.data['original_file']
            )

            new_heights = request.user.account_tier.heights.all()
            for new_h in new_heights:
                if image.get_original_height() > new_h.height:
                    thumbnail = Thumbnail.objects.create(
                        owner=request.user,
                        height=new_h.height,
                        link=request.data['original_file']
                    )
                    thumbnail.save()
                    image.thumbnails.add(thumbnail)

            image.save()
            serializer = ImageSerializer(
                image,
                fields=['owner', 'original_file', 'thumbnails'],
                context={'request': request}
            )
        elif request.data['temporary_link_create'] and request.data['duration']:
            if not request.user.account_tier.generate_links:
                raise PermissionDenied(
                    {'message': 'You do not have permission to generate temporary links'}
                )
            if not 30 < int(request.data['duration']) < 30000:
                raise ValidationError('Invalid duration range.')
            requested_image = Image.objects.get(id=request.data['temporary_link_create'])
            temp_link = TemporaryLink.objects.create(
                owner=request.user,
                hash=''.join(random.choices(string.ascii_lowercase, k=10)),
                path=requested_image.original_file,
                expires_in=request.data['duration']
            )
            temp_link.save()
            requested_image.temp_link = temp_link
            requested_image.save()

            serializer = ImageSerializer(
                requested_image,
                fields=['owner', 'original_file', 'temp_link', 'thumbnails'],
                context={'request': request}
            )
        else:
            serializer = ImageSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)

        return Response(serializer.data)


class AllImagesView(UserImagesView):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Image.objects.all()


def temp_link(request, slug):
    tmp_link = get_object_or_404(TemporaryLink, hash=slug)
    if tmp_link.valid_to < pytz.utc.localize(datetime.utcnow()):
        tmp_link.delete()
        return redirect('/')
    return redirect(f'{settings.MEDIA_URL}{tmp_link.path}')
