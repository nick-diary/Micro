from django.urls import path

from Micro import views

urlpatterns = [
    path('', views.Connexion.as_view(), name='connexion'),

    path('deconnexion', views.deconnexion, name='deconnexion'),
    path('membre', views.membre, name='membre'),
    path('membre/save', views.MembreSave.as_view(), name='membre_save'),
    path('membre/modifier/<int:pk>', views.MembreMod.as_view(), name='membre_mod'),
    path('membre/supprimer/<int:pk>', views.membre_supp, name='membre_supp'),
    path('caisse/save', views.CaisseSave.as_view(), name='caisse_save'),
    path('caisse', views.caisse, name='caisse'),
    path('cotisation', views.cotisation, name='cotisation'),
    path('reunion', views.reunion, name='reunion'),
    path('reunion/<int:pk>', views.ReunionDetailView.as_view(), name='reunion_detail'),
    path('reunion/create/', views.ReunionCreateView.as_view(), name='reunion_create'),
    path('pret', views.pret, name='pret'),
    path('pret/save', views.PretSave.as_view(), name='pret_save'),
    path('rembourser/<int:pk>', views.RembourserView.as_view(), name='rembourser'),
    path('rembourser/save/<int:pk>', views.RembourserSave.as_view(), name='rembourser_save'),
    path('clear-tables/', views.clear_tables, name='clear_tables'),
    path('new-week/', views.new_week, name='new_week'),
    path('reunion/penalite/<int:pk>', views.reunion_penal, name='reunion_penal')
]
