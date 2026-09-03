from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('APP', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE APP_cliente
                    ADD COLUMN senha VARCHAR(100) NOT NULL DEFAULT '',
                    CHANGE COLUMN ativo Usuario_ativo TINYINT(1) NOT NULL DEFAULT 1,
                    DROP COLUMN telefone,
                    DROP COLUMN data_nascimento;
            """,
            reverse_sql="""
                ALTER TABLE APP_cliente
                    ADD COLUMN telefone VARCHAR(20) NOT NULL DEFAULT '',
                    ADD COLUMN data_nascimento DATE NOT NULL DEFAULT '2000-01-01',
                    CHANGE COLUMN Usuario_ativo ativo TINYINT(1) NOT NULL DEFAULT 1,
                    DROP COLUMN senha;
            """,
        ),
    ]
