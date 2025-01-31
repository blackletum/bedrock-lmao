# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated by Django 4.2.18 on 2025-01-31 21:50

from django.db import migrations, models
import django.db.models.deletion
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0002_bedrockimage_bedrockrendition"),
        ("products", "0007_remove_monitorarticledetailpage_heading_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="monitorarticledetailpage",
            name="body",
        ),
        migrations.AddField(
            model_name="monitorarticledetailpage",
            name="call_to_action_middle",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="products.monitorcalltoactionsnippet"
            ),
        ),
        migrations.AddField(
            model_name="monitorarticledetailpage",
            name="summary",
            field=wagtail.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="monitorarticledetailpage",
            name="icon",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="cms.bedrockimage"),
        ),
    ]
