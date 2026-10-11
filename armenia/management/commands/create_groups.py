# armenia/management/commands/create_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


GROUPS = {
    "Superadmin": {
        "permissions": "__all__",
    },
    "Comision Administrativa": {
        "permissions": [
            "armenia.view_sesion", "armenia.add_sesion", "armenia.change_sesion", "armenia.delete_sesion",
            "armenia.view_sesionparticipante", "armenia.add_sesionparticipante",
            "armenia.change_sesionparticipante", "armenia.delete_sesionparticipante",
            "armenia.view_documento", "armenia.add_documento",
            "armenia.change_documento", "armenia.delete_documento",
            "armenia.view_noticia", "armenia.add_noticia",
            "armenia.change_noticia", "armenia.delete_noticia",
        ],
    },
    "Comision Financiera": {
        "permissions": [
            "armenia.view_movimientofinanciero", "armenia.add_movimientofinanciero",
            "armenia.change_movimientofinanciero", "armenia.delete_movimientofinanciero",
            "armenia.view_informefinancierosemanal", "armenia.add_informefinancierosemanal",
            "armenia.change_informefinancierosemanal", "armenia.delete_informefinancierosemanal",
        ],
    },
    "Comision Tecnica": {
        "permissions": [
            "armenia.view_temporada", "armenia.add_temporada",
            "armenia.change_temporada", "armenia.delete_temporada",
            "armenia.view_categoria", "armenia.add_categoria",
            "armenia.change_categoria", "armenia.delete_categoria",
            "armenia.view_equipo",
            "armenia.view_equipostemporadacategoria",
            "armenia.add_equipostemporadacategoria",
            "armenia.change_equipostemporadacategoria",
            "armenia.delete_equipostemporadacategoria",
            "armenia.view_jornada", "armenia.add_jornada",
            "armenia.change_jornada", "armenia.delete_jornada",
            "armenia.view_partido", "armenia.add_partido",
            "armenia.change_partido", "armenia.delete_partido",
            "armenia.view_vocalia", "armenia.add_vocalia",
            "armenia.change_vocalia", "armenia.delete_vocalia",
            "armenia.view_vocaliajugador", "armenia.add_vocaliajugador",
            "armenia.change_vocaliajugador", "armenia.delete_vocaliajugador",
        ],
    },
    "Comision Calificaciones": {
        "permissions": [
            "armenia.view_jugador", "armenia.add_jugador",
            "armenia.change_jugador", "armenia.delete_jugador",
            "armenia.view_jugadorequipotemporada",
            "armenia.add_jugadorequipotemporada",
            "armenia.change_jugadorequipotemporada",
            "armenia.delete_jugadorequipotemporada",
            "armenia.view_capitanequipotemporada",
            "armenia.add_capitanequipotemporada",
            "armenia.change_capitanequipotemporada",
            "armenia.delete_capitanequipotemporada",
            "armenia.view_documento", "armenia.add_documento",
        ],
    },
    "Comision Penas": {
        "permissions": [
            "armenia.view_sancion", "armenia.add_sancion",
            "armenia.change_sancion", "armenia.delete_sancion",
            "armenia.view_multa", "armenia.add_multa",
            "armenia.change_multa", "armenia.delete_multa",
            "armenia.view_recibo", "armenia.add_recibo",
            "armenia.change_recibo", "armenia.delete_recibo",
            "armenia.view_historialsancion", "armenia.add_historialsancion",
        ],
    },
    "Comision Seguro": {
        "permissions": [
            "armenia.view_lesion", "armenia.add_lesion",
            "armenia.change_lesion", "armenia.delete_lesion",
        ],
    },
    "Administrador Equipo": {
        "permissions": [
            "armenia.view_equipo",
            "armenia.view_jugador",
            "armenia.view_jugadorequipotemporada",
            "armenia.view_capitanequipotemporada",
            "armenia.view_partido",
            "armenia.view_vocalia",
            "armenia.view_sancion",
            "armenia.view_multa",
            "armenia.view_noticia",
        ],
    },
}


class Command(BaseCommand):
    help = "Crea los grupos base de la Liga Barrial La Armenia y les asigna permisos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina los permisos actuales de cada grupo antes de reasignarlos.",
        )

    def handle(self, *args, **options):
        reset = options["reset"]

        for group_name, config in GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            status = "creado" if created else "ya existía"

            if reset:
                group.permissions.clear()

            if config["permissions"] == "__all__":
                perms = list(Permission.objects.all())
            else:
                perms = self._resolve_permissions(config["permissions"])

            group.permissions.set(perms)
            self.stdout.write(self.style.SUCCESS(
                f"[{status}] {group_name} → {len(perms)} permisos"
            ))

        self.stdout.write(self.style.SUCCESS("\n✅ Grupos listos."))

    def _resolve_permissions(self, codes):
        """Devuelve una lista de objetos Permission a partir de códigos 'app.codename' o 'codename'."""
        resolved, missing = [], []

        for code in codes:
            if "." in code:
                app_label, codename = code.split(".", 1)
                try:
                    resolved.append(Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename,
                    ))
                except Permission.DoesNotExist:
                    missing.append(code)
            else:
                qs = Permission.objects.filter(codename=code)
                if qs.exists():
                    resolved.extend(list(qs))
                else:
                    missing.append(code)

        if missing:
            self.stdout.write(self.style.WARNING(
                f"⚠️  No encontrados: {', '.join(missing)}"
            ))

        return resolved