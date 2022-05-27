from images.models import PlanHeight, Plan


def run():
    h1 = PlanHeight.objects.create(height=200)
    h2 = PlanHeight.objects.create(height=400)
    h1.save()
    h2.save()

    plan1 = Plan.objects.create(
        name='Basic'
    )
    plan1.heights.add(h1)

    plan2 = Plan.objects.create(
        name='Premium',
        original_link=True
    )
    plan2.heights.add(h1, h2)

    plan3 = Plan.objects.create(
        name='Enterprise',
        original_link=True,
        generate_links=True
    )
    plan3.heights.add(h1, h2)

    plan1.save()
    plan2.save()
    plan3.save()