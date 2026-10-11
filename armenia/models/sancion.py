from django.db import models


class Sancion(models.Model):
    TIPOS = [
        ("jugador", "Jugador"),
        ("equipo", "Equipo"),
    ]
    ESTADOS = [
        ("activa", "Activa"),
        ("cumplida", "Cumplida"),
        ("apelada", "Apelada"),
        ("anulada", "Anulada"),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS)
    jugador = models.ForeignKey(
        "armenia.Jugador",
        on_delete=models.CASCADE,
        related_name="sanciones",
        blank=True, null=True,
    )
    equipo = models.ForeignKey(
        "armenia.Equipo",
        on_delete=models.CASCADE,
        related_name="sanciones",
        blank=True, null=True,
    )
    partido = models.ForeignKey(
        "armenia.Partido",
        on_delete=models.SET_NULL,
        related_name="sanciones",
        blank=True, null=True,
    )
    vocalia = models.ForeignKey(
        "armenia.Vocalia",
        on_delete=models.SET_NULL,
        related_name="sanciones",
        blank=True, null=True,
    )

    motivo = models.CharField(max_length=255)
    articulo = models.CharField(max_length=100, blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    dias = models.PositiveIntegerField(default=0)
    partidos_sancion = models.PositiveIntegerField(default=0)

    estado = models.CharField(max_length=20, choices=ESTADOS, default="activa")
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_sancion"
        verbose_name = "Sanción"
        verbose_name_plural = "Sanciones"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["estado"]), models.Index(fields=["tipo"])]

    def __str__(self):
        target = self.jugador or self.equipo
        return f"Sanción {self.get_tipo_display()} — {target} ({self.estado})"


class HistorialSancion(models.Model):
    sancion = models.ForeignKey(
        Sancion,
        on_delete=models.CASCADE,
        related_name="historial",
    )
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    motivo_cambio = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        blank=True, null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_historial_sancion"
        verbose_name = "Historial de sanción"
        verbose_name_plural = "Historial de sanciones"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sancion_id}: {self.estado_anterior} → {self.estado_nuevo}"


class Multa(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("pagada", "Pagada"),
        ("condonada", "Condonada"),
    ]
    FORMAS_PAGO = [
        ("efectivo", "Efectivo"),
        ("transferencia", "Transferencia"),
        ("deposito", "Depósito"),
        ("otro", "Otro"),
    ]

    sancion = models.ForeignKey(
        Sancion,
        on_delete=models.SET_NULL,
        related_name="multas",
        blank=True, null=True,
    )
    equipo = models.ForeignKey(
        "armenia.Equipo",
        on_delete=models.CASCADE,
        related_name="multas",
        blank=True, null=True,
    )

    monto = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    fecha_pago = models.DateField(blank=True, null=True)
    forma_pago = models.CharField(
        max_length=20, choices=FORMAS_PAGO, blank=True, null=True
    )
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_multa"
        verbose_name = "Multa"
        verbose_name_plural = "Multas"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["estado"])]

    def __str__(self):
        return f"Multa ${self.monto} — {self.motivo} ({self.estado})"


class Recibo(models.Model):
    multa = models.OneToOneField(
        Multa,
        on_delete=models.CASCADE,
        related_name="recibo",
    )
    numero = models.CharField(max_length=50, unique=True)
    entregado_a = models.CharField(max_length=150)
    entregado_por = models.CharField(max_length=150)
    fecha_entrega = models.DateField()
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_recibo"
        verbose_name = "Recibo"
        verbose_name_plural = "Recibos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Recibo {self.numero} — Multa {self.multa_id}"