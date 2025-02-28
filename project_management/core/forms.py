from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import Proyecto, Tarea, Mensaje, Comentario, User, Grupo, PerfilProyecto

class ProyectoForm(forms.ModelForm):
    grupos = forms.ModelMultipleChoiceField(
        queryset=Grupo.objects.all(),
        label="Grupos",
        help_text="Selecciona al menos un grupo para este proyecto.",
        required=True,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'fecha_inicio', 'fecha_fin', 'grupos']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise forms.ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")
        return cleaned_data

class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'fecha_limite', 'estado', 'usuarios_asignados']
        widgets = {
            'fecha_limite': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        proyecto = kwargs.pop('proyecto', None)  # Recibimos el proyecto desde la vista
        super().__init__(*args, **kwargs)
        if proyecto:
            # Limitar usuarios_asignados a miembros de los grupos del proyecto
            self.fields['usuarios_asignados'].queryset = User.objects.filter(
                grupos__proyecto=proyecto
            ).distinct()

    def clean_titulo(self):
        titulo = self.cleaned_data['titulo']
        if len(titulo) < 3:
            raise forms.ValidationError("El título debe tener al menos 3 caracteres.")
        return titulo

    def clean_descripcion(self):
        descripcion = self.cleaned_data['descripcion']
        if len(descripcion) < 5:
            raise forms.ValidationError("La descripción debe tener al menos 5 caracteres.")
        return descripcion

    def clean_fecha_limite(self):
        fecha_limite = self.cleaned_data['fecha_limite']
        from datetime import date
        if fecha_limite and fecha_limite < date.today():
            raise forms.ValidationError("La fecha límite no puede ser anterior a hoy.")
        return fecha_limite

class MensajeForm(forms.ModelForm):
    destinatario = forms.ModelChoiceField(queryset=User.objects.none())

    class Meta:
        model = Mensaje
        fields = ['destinatario', 'proyecto', 'contenido']  # Incluimos proyecto como opcional
        widgets = {
            'proyecto': forms.Select(attrs={'required': False}),  # No requerido
        }

    def __init__(self, *args, proyecto=None, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['destinatario'].queryset = User.objects.exclude(id=usuario.id)
        if proyecto:  # Si se pasa un proyecto, limitamos las opciones, pero no es obligatorio
            self.fields['proyecto'].queryset = Proyecto.objects.filter(usuarios_asignados=usuario)

    def clean_contenido(self):
        contenido = self.cleaned_data['contenido']
        if len(contenido) < 2:
            raise ValidationError("El mensaje debe tener al menos 2 caracteres.")
        if len(contenido) > 500:
            raise ValidationError("El mensaje no puede exceder los 500 caracteres.")
        return contenido

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_contenido(self):
        contenido = self.cleaned_data['contenido']
        if len(contenido) < 2:
            raise ValidationError("El comentario debe tener al menos 2 caracteres.")
        if len(contenido) > 300:
            raise ValidationError("El comentario no puede exceder los 300 caracteres.")
        return contenido

class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['nombre']

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if len(nombre) < 3:
            raise ValidationError("El nombre del grupo debe tener al menos 3 caracteres.")
        if Grupo.objects.filter(nombre=nombre, proyecto=self.instance.proyecto if self.instance.pk else None).exists():
            raise ValidationError("Ya existe un grupo con este nombre en el proyecto.")
        return nombre

class AsignarUsuarioGrupoForm(forms.ModelForm):
    class Meta:
        model = PerfilProyecto
        fields = ['usuario', 'rol']

    def __init__(self, *args, proyecto=None, grupo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto
        self.grupo = grupo

    def clean(self):
        cleaned_data = super().clean()
        usuario = cleaned_data.get('usuario')
        rol = cleaned_data.get('rol')
        if usuario and rol and self.proyecto and self.grupo:
            if PerfilProyecto.objects.filter(
                usuario=usuario, 
                proyecto=self.proyecto, 
                grupo=self.grupo
            ).exists():
                raise ValidationError("Este usuario ya está asignado a este grupo en el proyecto.")
        return cleaned_data

# (Otros formularios existentes)

class CrearUsuarioForm(UserCreationForm):
    rol = forms.ChoiceField(
        choices=PerfilProyecto.ROLES,
        label=_("Rol"),
        help_text=_("Selecciona el rol inicial del usuario."),
        required=True
    )
    proyecto = forms.ModelChoiceField(
        queryset=Proyecto.objects.all(),
        label=_("Proyecto"),
        help_text=_("Selecciona un proyecto (opcional)."),
        required=False  # Aseguramos que sea opcional
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'rol', 'proyecto']
        labels = {
            'username': _("Nombre de usuario"),
            'email': _("Correo electrónico"),
            'password1': _("Contraseña"),
            'password2': _("Confirmar contraseña"),
        }
        help_texts = {
            'username': _("Mínimo 4 caracteres. Solo letras, números y @/./+/-/_"),
            'email': _("Introduce una dirección de correo válida."),
            'password1': _("Tu contraseña debe tener al menos 8 caracteres y no puede ser demasiado común."),
            'password2': _("Repite la contraseña para confirmarla."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar mensajes de error y ayuda para contraseñas en español
        self.fields['password1'].help_text = _("Tu contraseña debe tener al menos 8 caracteres y no puede ser demasiado común.")
        self.fields['password2'].help_text = _("Repite la contraseña para confirmarla.")
        self.error_messages = {
            'password_mismatch': _("Las contraseñas no coinciden."),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 4:
            raise ValidationError(_("El nombre de usuario debe tener al menos 4 caracteres."))
        if User.objects.filter(username=username).exists():
            raise ValidationError(_("Este nombre de usuario ya está en uso."))
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError(_("El correo electrónico es obligatorio."))
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Este correo electrónico ya está registrado."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            rol = self.cleaned_data['rol']
            proyecto = self.cleaned_data.get('proyecto')
            if proyecto:  # Solo crear PerfilProyecto si se seleccionó un proyecto
                PerfilProyecto.objects.create(usuario=user, proyecto=proyecto, rol=rol)
        return user