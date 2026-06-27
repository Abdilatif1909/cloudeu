from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quizzes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="quiz",
            name="pass_score",
            field=models.PositiveSmallIntegerField(default=70),
        ),
        migrations.AddField(
            model_name="quiz",
            name="question_timer_seconds",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="quiz",
            name="randomize_questions",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="quiz",
            name="shuffle_answers",
            field=models.BooleanField(default=True),
        ),
    ]
