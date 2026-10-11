from django.db import models


class Sesion(models.Model):
    TIPOS = [
        ("ordinaria", "Ordinaria"),
        ("extraordinaria", "Extraordinaria"),
    ]
    ESTADOS = [
        ("programada", "Programada"),
        ("en_curso", "En curso"),
        ("finalizada", "Finalizada"),
        ("cancelada", "Cancelada"),
    ]

    fecha = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default="ordinaria")
    orden_del_dia = models.TextField(blank=True, null=True)
    acta = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="programada")
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_sesion"
        verbose_name = "Sesión"
        verbose_name_plural = "Sesiones"
        ordering = ["-fecha"]
        indexes = [models.Index(fields=["fecha"]), models.Index(fields=["estado"])]

    def __str__(self):
        return f"Sesión {self.get_tipo_display()} — {self.fecha}"


class SesionParticipante(models.Model):
    sesion = models.ForeignKey(
        Sesion,
        on_delete=models.CASCADE,
        related_name="participantes",
    )
    nombre = models.CharField(max_length=150)
    cargo = models.CharField(max_length=150, blank=True, null=True)
    presente = models.BooleanField(default=True)
    observaciones = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_sesion_participante"
        verbose_name = "Participante de sesión"
        verbose_name_plural = "Participantes de sesión"
        ordering = ["sesion", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.sesion})"


class Documento(models.Model):
    TIPOS = [
        ("cedula", "Cédula"),
        ("acta", "Acta"),
        ("factura", "Factura"),
        ("informe", "Informe"),
        ("carnet", "Carnet"),
        ("otro", "Otro"),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.CharField(
        max_length=500,
        help_text="Ruta o URL del archivo. No se almacena el archivo en BD.",
    )
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    tamano_bytes = models.PositiveIntegerField(blank=True, null=True)

    # Relaciones opcionales según contexto
    jugador = models.ForeignKey(
        "armenia.Jugador",
        on_delete=models.SET_NULL,
        related_name="documentos",
        blank=True, null=True,
    )
    equipo = models.ForeignKey(
        "armenia.Equipo",
        on_delete=models.SET_NULL,
        related_name="documentos",
        blank=True, null=True,
    )
    sesion = models.ForeignKey(
        Sesion,
        on_delete=models.SET_NULL,
        related_name="documentos",
        blank=True, null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_documento"
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["tipo"])]

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.titulo}"


class Noticia(models.Model):
    titulo = models.CharField(max_length=255)
    resumen = models.CharField(max_length=500, blank=True, null=True)
    contenido = models.TextField()
    imagen = models.CharField(max_length=500, blank=True, null=True)
    autor = models.CharField(max_length=150, blank=True, null=True)
    publicada = models.BooleanField(default=False)
    destacada = models.BooleanField(default=False)
    fecha_publicacion = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_noticia"
        verbose_name = "Noticia"
        verbose_name_plural = "Noticias"
        ordering = ["-fecha_publicacion", "-created_at"]
        indexes = [
            models.Index(fields=["publicada"]),
            models.Index(fields=["destacada"]),
        ]

    def __str__(self):
        return self.titulo