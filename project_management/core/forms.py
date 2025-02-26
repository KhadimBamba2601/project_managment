from django import forms
from .models import Proyecto, Tarea, Mensaje, Comentario, User, Grupo, PerfilProyecto

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'fecha_limite', 'estado']
        widgets = {
            'fecha_limite': forms.DateInput(attrs={'type': 'date'}),
        }

class MensajeForm(forms.ModelForm):
    destinatario = forms.ModelChoiceField(queryset=User.objects.none())  # Se llenará dinámicamente

    class Meta:
        model = Mensaje
        fields = ['destinatario', 'contenido']

    def __init__(self, *args, proyecto=None, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if proyecto and usuario:
            # Filtra los destinatarios a usuarios asignados al proyecto, excluyendo al remitente
            self.fields['destinatario'].queryset = proyecto.usuarios_asignados.exclude(id=usuario.id)

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 3}),
        }

class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['nombre']

class AsignarUsuarioGrupoForm(forms.ModelForm):
    class Meta:
        model = PerfilProyecto
        fields = ['usuario', 'rol']