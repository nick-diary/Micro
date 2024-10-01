from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum , F, Q
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


from Micro.models import Membre, Reunion, Verser, Caisse, Assist , Pret, Remboursement, Tampon, Semaine


# Create your views here.
# class Connexion(View):
#     @staticmethod
#     def get(request):
#         if request.user.is_authenticated:
#             return redirect('caisse')  # or any other appropriate page
#         return render(request, 'connexion.html')

#     @staticmethod
#     def post(request):
#         nom = request.POST['UsernameCompte']
#         mot = request.POST['MotPasseCompte']
#         try:
#             user = User.objects.get(username=nom)
#             check_pass = check_password(mot, user.password)
#             if check_pass:
#                 user = authenticate(request, username=nom, password=mot)
#                 login(request, user)
#                 return redirect('caisse')
#             else:
#                 messages.error(request, 'Mot de passe incorrect')
#         except User.DoesNotExist:
#             messages.error(request, f'Votre nom d\'utilisateur n\'existe pas !')
#         return render(request, 'connexion.html')
class Connexion(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            return redirect('caisse')  # or any other appropriate page
        return render(request, 'connexion.html')

    @staticmethod
    def post(request):
        nom = request.POST['UsernameCompte']
        mot = request.POST['MotPasseCompte']
        try:
            user = User.objects.get(username=nom)
            check_pass = check_password(mot, user.password)
            now = timezone.now()
            if now.weekday() == 6 :
                return JsonResponse({
                    'success': False,
                    'message': 'Tsy afaka misokatra ny application satria alahady androany ' + str(now.date().strftime('%d %b %Y')),
                    'redirect': '/'  # Assurez-vous que c'est le bon chemin
                 })
            
            elif check_pass:
                user = authenticate(request, username=nom, password=mot)
                login(request, user)
            
                return JsonResponse({
                    'success': True,
                    'message': 'Connexion réussie !',
                    'redirect': '/caisse'  # Assurez-vous que c'est le bon chemin
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Mot de passe incorrect'
                })
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Votre nom d\'utilisateur n\'existe pas !'
            })

def deconnexion(request):
    logout(request)
    return redirect('connexion')

@login_required
def membre(request):
    active_membre = 'active'
    # membres = Membre.objects.all().order_by('nom_membre', 'prenom_membre')

    #total penalite
    assist = Assist.objects.all()
    # total_penalite = sum(1 for a in assist if not a.assister) * 500

    #total cotisation
    verser = Verser.objects.select_related('membre').all()
    total_montant_cotisation = sum(v.montant_verser for v in verser)

    #total caisse
    caisse = Caisse.objects.filter(date_fin__gt=timezone.now()).first()
    montant_caisse = caisse.montant_caisse if caisse else 0
    # total_caisse = total_penalite + montant_caisse

    #get revenue
    nb_tampon = total_montant_cotisation / 1000

    if nb_tampon == 0:
       revenue_tampon = 0
    else:
        revenue_tampon = montant_caisse / nb_tampon
    #all membrers  
    membres = Membre.objects.annotate(total_verser=Sum('verser__montant_verser')/1000).annotate(total_revenue=F('total_verser') * (revenue_tampon)).order_by('nom_membre', 'prenom_membre')



    context = {
        'active_membre': active_membre,
        'membres': membres,
        'revenue_tampon': revenue_tampon,
        
    }

    return render(request, 'membre_list.html', context)

@method_decorator(login_required, name='dispatch')
# class MembreSave(View):
#     @staticmethod
#     def get(request):
#         return render(request, 'membre_save.html')

#     @staticmethod
#     def post(request):
#         nom_membre = request.POST['nom_membre']
#         prenom_membre = request.POST['prenom_membre']
#         activite_membre = request.POST['activite_membre']

#         Membre.objects.create(
#             nom_membre=nom_membre,
#             prenom_membre=prenom_membre,
#             activite_membre=activite_membre
#         )

#         messages.success(request, 'Enregistrer avec succès !')
#         return redirect('membre')
class MembreSave(View):
    @staticmethod
    def get(request):
        return render(request, 'membre_save.html')

    @staticmethod
    def post(request):
        try:
            nom_membre = request.POST['nom_membre']
            prenom_membre = request.POST['prenom_membre']
            activite_membre = request.POST['activite_membre']
            
            Membre.objects.create(
                nom_membre=nom_membre,
                prenom_membre=prenom_membre,
                activite_membre=activite_membre
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Membre enregistré avec succès !',
                'redirect': '/membre'  # Assurez-vous que c'est le bon chemin
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de l\'enregistrement : {str(e)}'
            })

@method_decorator(login_required, name='dispatch')
class MembreMod(View):
    @staticmethod
    def get(request, pk):
        membre = get_object_or_404(Membre, pk=pk)
        return render(request, 'membre_edit.html', {'membre': membre})

    @staticmethod
    def post(request, pk):
        membre = get_object_or_404(Membre, pk=pk)


        nom_membre = request.POST['nom_membre']
        prenom_membre = request.POST['prenom_membre']
        activite_membre = request.POST['activite_membre']

        membre.nom_membre = nom_membre
        membre.prenom_membre = prenom_membre
        membre.activite_membre = activite_membre
        membre.save()
        return JsonResponse({'message': "Modification réussie"})
        # return JsonResponse({'message': "Modification réussie"})



# @require_POST
@login_required
def membre_supp(request,pk):
    # membre_id = request.GET.get('id')
    try:
        membre = Membre.objects.get(pk=pk)
        membre.delete()
        return JsonResponse({'success': True})
    except Membre.DoesNotExist:
        return JsonResponse({'success': False})



@login_required
def reunion(request):
    active_reunion = 'active'
    reunions = Reunion.objects.all().order_by('-pk')  # Get all reunions, newest first
    assist = Assist.objects.all()
    #count penalite
    # total_penalite = sum(a.assister for a in assist) * 500
    #count assister
    total_penalite = sum(1 for a in assist if not a.assister and a.penalite) * 500

    current_date = timezone.now().date()
    weekDay = current_date.weekday()
    last_reunion = reunions.first()
    if last_reunion and current_date > last_reunion.date_reunion.date():
        add_reunion = True
    elif not last_reunion:
        add_reunion = True
    else:
        add_reunion = False

    context = {
        'active_reunion': active_reunion,
        'reunions': reunions,
        'total_penalite': total_penalite,
        'current_date' : current_date,
        'weekDay' : weekDay,
        'add_reunion' : add_reunion

    }
    return render(request, 'reunion_list.html', context)




@method_decorator(login_required, name='dispatch')
class ReunionDetailView(View):
    @staticmethod
    def get(request, pk):
        reunion = get_object_or_404(Reunion, pk=pk)
        current_date = timezone.now().weekday()
        date_reunion = reunion.date_reunion
        attended_members_ids = Assist.objects.filter(reunion=reunion).values_list('membre_id', flat=True)
        
        # Filter members based on attended members
        membres = Membre.objects.filter(id__in=attended_members_ids)
        assists = Assist.objects.filter(reunion=reunion)  # Get existing attendance

        context = {
            'current_date': current_date,
            'date_reunion' : date_reunion,
            'membres': membres,
            'assists': assists,
            'reunion': reunion,
        }

        return render(request, 'reunion_detail.html', context)

    @staticmethod
    def post(request, pk):
        reunion = get_object_or_404(Reunion, pk=pk)

        # Update or create attendance records
        for membre in Membre.objects.all():
            assister = request.POST.get(f'assister_{membre.id}') == '1'
            penalite = request.POST.get(f'penalite_{membre.id}') == '1'
            
            Assist.objects.update_or_create(
                reunion=reunion,
                membre=membre,
                defaults={'assister': assister, 'penalite': penalite}
            )

        return JsonResponse({'message': "Modification réussie"})
  



@method_decorator(login_required, name='dispatch')

class ReunionCreateView(View):
    model = Reunion
    success_url = reverse_lazy('reunion')

    def get(self, request, *args, **kwargs):
        current_date = timezone.now()
        weekDay = current_date.weekday()
        membres = Membre.objects.all()
        context = {
            'current_date': current_date,
            'membres': membres,
            'current_date' : current_date
        }
        return render(request, 'reunion_new.html', context)

    def post(self, request, *args, **kwargs):
        now = timezone.now().date()
        
        # Try to get the latest reunion or create a new one if none exists
        try:
            reunion = Reunion.objects.latest('date_reunion')
            if now != reunion.date_reunion:
                reunion = Reunion(date_reunion=now)
                reunion.save()
        except Reunion.DoesNotExist:
            # Create a new reunion if none exists
            reunion = Reunion(date_reunion=now)
            reunion.save()
        
        # Loop through all members and create Assist instances
        for membre in Membre.objects.all():
            assister = request.POST.get(f'assister_{membre.id}') == '1'
            penalite = not assister  # Penalite is true if not assisting
            
            Assist.objects.create(
                reunion=reunion,
                membre=membre,
                assister=assister,
                penalite=penalite
            )
        
        return JsonResponse({'success': True, 'redirect_url': self.success_url})
# class ReunionCreateView(CreateView):
#     model = Reunion
#     template_name = 'reunion_new.html'
#     fields = []  # We'll set the date in the form_valid method
#     success_url = reverse_lazy('reunion')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['current_date'] = timezone.now() + timedelta(hours=3)
#         context['membres'] = Membre.objects.all()
#         return context


#     def form_valid(self, form):
#         form.instance.date_reunion = timezone.now()
#         response = super().form_valid(form)
#         for membre in Membre.objects.all():
#             assister = self.request.POST.get(f'assister_{membre.id}') == '1'
#             penalite = self.request.POST.get(f'penalite_{membre.id}') == '1'
#             Assist.objects.create(
#                 reunion=self.object, 
#                 membre=membre, 
#                 assister=assister, 
#                 penalite=penalite
#             )
#         return response


@login_required
def cotisation(request):

    activate_verser = 'active'
    verser = Verser.objects.select_related('membre').all()
    total_montant = sum(v.montant_verser for v in verser)
    context = {
        'activate_verser': activate_verser,
        'verser': verser,
        'total_montant': total_montant,
    }
    return render(request, 'cotisation.html', context)


def calculate_loan_repayment(pret):
    total_remboursement = 0
    interest = pret.montant_pret * 0.10  # 10% of the loan amount
    
    # Get all repayments for this loan
    remboursements = Remboursement.objects.filter(id_pret=pret.pk)
    
    # Sum up all repayments
    for remboursement in remboursements:
        total_remboursement += remboursement.montant_rembours
    
    # Calculate the remaining balance
    remaining_balance =  total_remboursement - pret.montant_pret  + interest
    
    # return {
    #     'total_remboursement': total_remboursement,
    #     'interest': interest,
    #     'remaining_balance': remaining_balance
    # }
    return remaining_balance

@login_required
def caisse(request):
    active_caisse = 'active'

    #nombre de membres
    nb_membres = Membre.objects.all().count()

    #total pret non rembourser
    if Pret.objects.exists() :
        pret_non_paye = Pret.objects.aggregate(Sum('montant_rembouresser'))['montant_rembouresser__sum']
    else:
        pret_non_paye = 0

    #total penalite
    assist = Assist.objects.all()
    total_penalite = sum(1 for a in assist if not a.assister and not a.penalite) * 500
    rest_penalite = sum(1 for a in assist if not a.assister and a.penalite) * 500
    #total cotisation
    verser = Verser.objects.select_related('membre').all()
    total_montant_cotisation = sum(v.montant_verser for v in verser)

    # total_caisse = total_penalite + total_montant_cotisation
    caisse = Caisse.objects.filter(date_fin__gt=timezone.now()).first()
    montant_caisse = caisse.montant_caisse if caisse else 0
    total_caisse = montant_caisse

    nb_tampon = total_montant_cotisation / 1000
    if nb_tampon == 0:
       revenue_tampon = 0
    else:
        revenue_tampon = total_caisse / nb_tampon


      # Calcul des remboursements de prêts
    all_loans = Pret.objects.all()
    total_benefit = 0
    loan_results = []
    total_repaid = 0
    total_interest = 0
    total_remaining = 0
    
    for loan in all_loans:
        total_benefit  += calculate_loan_repayment(loan)

        # result = calculate_loan_repayment(loan)
        # loan_results.append({
        #     'loan_id': loan.id,
        #     'total_repaid': result['total_remboursement'],
        #     'interest': result['interest'],
        #     'remaining_balance': result['remaining_balance']
        # })
        # total_repaid += result['total_remboursement']
        # total_interest += result['interest']
        # total_remaining += result['remaining_balance']
    
    # if timezone.now().weekday() == 0 :
    #     date_deb = timezone.now()
    #     date_fin = date_deb + timedelta(days=4)
    #     Semaine.objects.create(
    #         date_deb = date_deb,
    #         date_fin = date_fin
    #     )

    #------ Ajout d'une nouvelle semaine ----
    semaine = Semaine.objects.order_by('-date_fin').first()
    now = timezone.now().date() # This will give you a datetime.date object

    if (semaine.date_fin) < now and now.weekday() <= 5:
        last_monday = now - timedelta(days=now.weekday())
        # Calculate date_fin as 5 days after now
        date_fin = last_monday + timedelta(days=5)

        Semaine.objects.create(
            date_deb = last_monday,
            date_fin = date_fin
        )


    context = {
        'active_caisse': active_caisse,
        'total_caisse': total_caisse,
        'total_montant_cotisation' : total_montant_cotisation,
        'total_penalite' : total_penalite,
        'nb_membres' : nb_membres,
        'revenue_tampon' : revenue_tampon,
        'pret_non_paye' : pret_non_paye,
        'rest_penalite' : rest_penalite,
        'nb_tampon' : int(nb_tampon)

        # 'loan_results': loan_results,
        # 'total_repaid': total_repaid,
        # 'total_interest': total_interest,
        # 'total_remaining': total_remaining,

    }
    return render(request, 'caisse.html', context)

def verser(request):
    active_verser = 'active'
    verser = Verser.objects.all()
    context = {
        'active_verser': active_verser,
        'verser': verser
    }
    return render(request, 'caisse.html', context)
    
def pret(request):
    activate_pret = 'active'
    pret = Pret.objects.select_related('membre').all()

    context = {
        'activate_pret': activate_pret,
        'pret': pret
    }
    return render(request, 'pret.html', context)

# class PretSave(View):
#     @staticmethod
#     def get(request):
#         listes_membre = Membre.objects.all()
#         context = {
#             'listes_membre': listes_membre
#         }
#         return render(request, 'pret_save.html', context)

#     @staticmethod
#     def post(request):
#         try:
#             membre_id = request.POST['membre_id']
#             montant_preter = float(request.POST['montant_preter'])
#             montant_rembouresser = montant_preter * 1.1

#             # membre = Membre.objects.get(pk=membre_id)

          
#             # Vérifier s'il y a une caisse active sinon en créer une
#             caisses = Caisse.objects.filter(date_fin__gt=timezone.now()).first()
#             if not caisses:
#                 Caisse.objects.create(
#                     date_deb=timezone.now(),
#                     date_fin=timezone.now() + timedelta(days=180),
#                     montant_caisse=montant_preter
#                 )
#             else:
#                 caisses.montant_caisse -= montant_preter
#                 caisses.save()

#               # Enregistrer le versement
#             membre_instance = Membre.objects.get(id=int(membre_id))
#             caisse_id = Caisse.objects.get(id=int(caisses.pk))
#             prets = Pret.objects.get(membre=membre_instance)
#             if not prets.exists() or prets.montant_rembouresser == 0 :
#                 Pret.objects.create(
#                     date_pret=timezone.now(),
#                     date_rembourser=timezone.now() + timedelta(days=90),
#                     membre=membre_instance,
#                     montant_pret=montant_preter,
#                     montant_rembouresser=montant_rembouresser,
#                     caisse=caisse_id
#                 )
#                 messages.success(request, 'Enregistrement avec succès du prêt de ' + str(montant_preter) +'ar de ' + membre_instance.nom_membre + ' ' + membre_instance.prenom_membre)
#             else:
#                 messages.success(request, 'Mbola misy ' + prets.montant_rembouresser + 'ar tsy voaloan\'i ' + membre_instance.nom_membre + ' ' + membre_instance.prenom_membre +' t@ prêt du ' + str(prets.date_pret))

#             # Mettre à jour les tampons du membre
#             # membres.nb_tampom += tampon
#             # membres.save()
            
            
#             # return render(request, 'cotisation.html')
#             return redirect('pret')

#         except Membre.DoesNotExist:
#             messages.error(request, 'Membre non trouvé')
#             # return render(request, 'cotisation.html')
#             return redirect('pret')

#         except Exception as e:
#             messages.error(request, f'Erreur lors de l\'enregistrement : {str(e)}')
#             # return render(request, 'cotisation.html')
#             return redirect('pret')


@method_decorator(login_required, name='dispatch')
# class CaisseSave(View):
#     @staticmethod
#     def get(request):
#         listes_membre = Membre.objects.all()
#         context = {
#             'listes_membre': listes_membre
#         }
#         return render(request, 'cotisation_save.html', context)

#     @staticmethod
#     def post(request):
#         try:
#             membre_id = request.POST['membre_id']
#             montant_verser = float(request.POST['montant_verser'])

#             # membre = Membre.objects.get(pk=membre_id)

#             # Calcul du nombre de tampons
#             tampon = montant_verser / 1000

#             # Enregistrer le versement
#             membre_instance = Membre.objects.get(id=int(membre_id))
#             Verser.objects.create(
#                 date_versement=timezone.now(),
#                 membre=membre_instance,
#                 montant_verser=montant_verser
#             )

#             # Vérifier s'il y a une caisse active sinon en créer une
#             caisses = Caisse.objects.filter(date_fin__gt=timezone.now()).first()
#             if not caisses:
#                 Caisse.objects.create(
#                     date_deb=timezone.now(),
#                     date_fin=timezone.now() + timedelta(days=180),
#                     montant_caisse=montant_verser
#                 )
#             else:
#                 caisses.montant_caisse += montant_verser
#                 caisses.save()

            
#             messages.success(request, 'Enregistré avec succès !')
#             # return render(request, 'cotisation.html')
#             return redirect('cotisation')

#         except Membre.DoesNotExist:
#             messages.error(request, 'Membre non trouvé')
#             # return render(request, 'cotisation.html')
#             return redirect('cotisation')

#         except Exception as e:
#             messages.error(request, f'Erreur lors de l\'enregistrement : {str(e)}')
#             # return render(request, 'cotisation.html')
#             return redirect('cotisation')
#         except KeyError as e:
#         # Handle missing POST parameters
#             messages.error(request, 'Membre non trouvé')

#             return redirect('cotisation')
#         except Exception as e:
#         # Handle any other exceptions
#             messages.error(request, 'Membre non trouvé')
#             return redirect('cotisation')
class CaisseSave(View):
    @staticmethod
    def get(request):
        listes_membre = Membre.objects.all()
        context = {
            'listes_membre': listes_membre
        }
        return render(request, 'cotisation_save.html', context)

    @staticmethod
    def post(request):
        try:
            membre_id = request.POST['membre_id']
            montant_verser = float(request.POST['montant_verser'])
            
            # Calcul du nombre de tampons
            nb_tampon = montant_verser / 1000
            
            # Enregistrer le versement
            membre_instance = Membre.objects.get(id=int(membre_id))
            semaine= Semaine.objects.order_by('-date_fin').first()
            now = timezone.now().date()
            msg = ''

            # Check if there are any instances of Tampon
            if not Tampon.objects.filter(Q(membre=membre_instance) & Q(semaine=semaine)).exists() :
                Verser.objects.create(
                    date_versement=timezone.now(),
                    membre=membre_instance,
                    montant_verser=montant_verser
                )
                Tampon.objects.create(
                    nb_tampon = nb_tampon,
                    membre = membre_instance,
                    semaine = semaine
                )
                # Vérifier s'il y a une caisse active sinon en créer une
                caisses = Caisse.objects.filter(date_fin__gt=timezone.now()).first()
                if not caisses:
                    Caisse.objects.create(
                        date_deb=timezone.now(),
                        date_fin=timezone.now() + timedelta(days=180),
                        montant_caisse=montant_verser
                    )
                else:
                    caisses.montant_caisse += montant_verser
                    caisses.save()
                msg = 'Voaray ny cotisation ' + str(int(montant_verser)) + 'ar an\'i ' + membre_instance.nom_membre + " " + membre_instance.prenom_membre
                redirect = '/cotisation'
                return JsonResponse({
                    'success': True,
                    'message': msg,
                    'redirect': redirect  # Assurez-vous que c'est le bon chemin
                })
            else:
                # Calculate the sum of nb_tampon for the specified membre
                total_nb_tampon = Tampon.objects.filter(Q(membre=membre_instance) & Q(semaine=semaine)).aggregate(total=Sum('nb_tampon'))

                # Access the total
                total_value = total_nb_tampon['total']
                rest_tampon = int(5 - total_value)

                if semaine.date_deb <= now <= semaine.date_fin and nb_tampon <= rest_tampon :
                    Verser.objects.create(
                        date_versement=timezone.now(),
                        membre=membre_instance,
                        montant_verser=montant_verser
                    )
                    Tampon.objects.create(
                        nb_tampon = nb_tampon,
                        membre = membre_instance,
                        semaine = semaine
                    )
                     # Vérifier s'il y a une caisse active sinon en créer une
                    caisses = Caisse.objects.filter(date_fin__gt=timezone.now()).first()
                    if not caisses:
                        Caisse.objects.create(
                            date_deb=timezone.now(),
                            date_fin=timezone.now() + timedelta(days=180),
                            montant_caisse=montant_verser
                        )
                    else:
                        caisses.montant_caisse += montant_verser
                        caisses.save()
                    msg = 'Voaray ny cotisation ' + str(int(montant_verser)) + 'ar an\'i ' + membre_instance.nom_membre + " " + membre_instance.prenom_membre
                    redirect = '/cotisation'
                    return JsonResponse({
                        'success': True,
                        'message': msg,
                        'redirect': redirect  # Assurez-vous que c'est le bon chemin
                    })
                else:
                    msg = '5000Ar isan-kerinandro ihany no azo atao ry '  + membre_instance.nom_membre + " " + membre_instance.prenom_membre + ' !\t Efa mandoa ' + str(total_value*1000) + 'ar ianao!\n ' + str(abs(rest_tampon*1000)) + 'ar sisa no azonao atao @ ty semaine ty' if rest_tampon != 0 else '@ herinandro indray vao afaka manao cotisation i '  + membre_instance.nom_membre + " " + membre_instance.prenom_membre + ' fa efa nahafeno cotisation 5000ar !'
                    redirect = '/cotisation' if rest_tampon == 0 else ''
                    return JsonResponse({
                        'success': False,
                        'message': msg,
                        'redirect': redirect  # Assurez-vous que c'est le bon chemin
                    })
            # return JsonResponse({
            #     'success': True,
            #     'message': msg,
            #     'redirect': redirect  # Assurez-vous que c'est le bon chemin
            # })
        except Membre.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Membre non trouvé'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de l\'enregistrement : {str(e)}'
            })

@login_required
def pret(request):
    activate_pret = 'active'
    pret = Pret.objects.select_related('membre').all()
    caisse = Caisse.objects.filter(date_fin__gt=timezone.now()).first()
    context = {
        'activate_pret': activate_pret,
        'pret': pret,
        'montant_caisse': caisse.montant_caisse if caisse else 0
    }
    return render(request, 'pret.html', context)


@method_decorator(login_required, name='dispatch')
class PretSave(View):
    @staticmethod
    def get(request):
        listes_membre = Membre.objects.all()
        total_montant_caisse = Caisse.objects.aggregate(Sum('montant_caisse'))['montant_caisse__sum']
        print(total_montant_caisse)        
        context = {
            'listes_membre': listes_membre,
            'montant_caisse': int(total_montant_caisse)
        }
        return render(request, 'pret_save.html', context)


    @staticmethod
    def post(request):
        try:
            membre_id = request.POST['membre_id']
            montant_preter = float(request.POST['montant_preter'])
            
            # Check if the member has an outstanding loan
            membre = Membre.objects.get(id=int(membre_id))
            pret = Pret.objects.filter(membre=membre).order_by('-date_pret').first()
            
            if pret and pret.montant_rembouresser > 0:
                return JsonResponse({
                    'status': 'error',
                    'message': f'{membre.nom_membre} {membre.prenom_membre} a encore un prêt non remboursé dont le reste à payer est {int(pret.montant_rembouresser)}ar .'
                })

            montant_moins_caisse = montant_preter - (montant_preter / 10)
            
            # Check for active cash register or create a new one
            caisses = Caisse.objects.filter(date_fin__gt=timezone.now()).first()
            if not caisses:
                caisses = Caisse.objects.create(
                    date_deb=timezone.now(),
                    date_fin=timezone.now() + timedelta(days=180),
                    montant_caisse=montant_moins_caisse
                )
            elif caisses.montant_caisse < montant_moins_caisse:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Montant insuffisant dans la caisse'
                })
            else:
                caisses.montant_caisse -= montant_moins_caisse
                caisses.save()

            # Create the new loan
            Pret.objects.create(
                date_pret=timezone.now(),
                montant_pret=montant_preter,
                etat_pret=False,
                montant_rembouresser= montant_preter*1.1,
                montant_paye = montant_moins_caisse,
                membre=membre,
                caisse=caisses
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Prêt enregistré avec succès!'
            })

        except Membre.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Membre non trouvé'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erreur lors de l\'enregistrement : {str(e)}'
            })

@method_decorator(login_required, name='dispatch')
class RembourserView(View):
    @staticmethod
    def get(request, pk):
        # Your view logic here
        rembourser = Remboursement.objects.select_related('id_membre').filter(id_pret=pk)
        # membre = rembourser.first().id_membre if rembourser.exists() else None
        pret = Pret.objects.get(pk=pk)
        membre = pret.membre
        context={
            'rembourser': rembourser,
            'current_pk': pk,
            'montant_rembouresser': pret.montant_rembouresser,
            'nom_membre': f"{membre.nom_membre} {membre.prenom_membre}",
        }
        return render(request, 'rembourser.html', context)


@method_decorator(login_required, name='dispatch')
class RembourserSave(View):
    @staticmethod
    def get(request, pk):
        pret = Pret.objects.get(id=int(pk))
        membre =pret.membre
        montant_max = pret.montant_rembouresser
        context ={
                    'pret': pret,
                    'current_pk': pk,
                    'montant_max': int(montant_max),
                    'nom_membre': f"{membre.nom_membre} {membre.prenom_membre}",
                   }
        return render(request, 'rembours_save.html',context )

    @staticmethod
    def post(request, pk):
        pret = get_object_or_404(Pret, pk=pk)
        try:
            montant_rembours = float(request.POST['montant_rembours'])

            # Vérifier s'il y a déjà un remboursement pour ce prêt
            remboursements_existants = Remboursement.objects.filter(id_pret=pret).exists()

            # Calculer le reste à payer

            reste_paye = max(0, pret.montant_rembouresser - montant_rembours)
            reste_paye *= 1.1

            # Mettre à jour ou créer une caisse
            caisse = Caisse.objects.filter(date_fin__gt=timezone.now()).first()
            if not caisse:
                caisse = Caisse.objects.create(
                    date_deb=timezone.now(),
                    date_fin=timezone.now() + timedelta(days=180),
                    montant_caisse=montant_rembours
                )
            else:
                caisse.montant_caisse += montant_rembours
                caisse.save()

            # Enregistrer le remboursement
            reste_paye = round(reste_paye,0) if reste_paye > 1 else 0
            Remboursement.objects.create(
                date_rembours=timezone.now(),
                id_membre=pret.membre,
                id_pret=pret,
                montant_rembours=montant_rembours,
                reste_paye=reste_paye,
            )

            # Mettre à jour le prêt
            pret.montant_rembouresser = reste_paye
            if reste_paye == 0:
                pret.etat_pret = True
            pret.save()

            # Ajouter 10% si c'est le premier remboursement
            # if not remboursements_existants:
            pret.montant_rembouresser = reste_paye
            pret.save()
            messages.success(request, f'Remboursement de {int(montant_rembours)} ar enregistré avec succès !')
            return redirect('rembourser', pk=pk)
        except Membre.DoesNotExist:
            messages.error(request, 'Membre non trouvé')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'enregistrement : {str(e)}')
        return redirect('rembourser', pk=pk)




@login_required
@require_POST
@csrf_exempt
def clear_tables(request):
    password = request.POST.get('password')
    user = authenticate(username=request.user.username, password=password)
    
    if user is not None:
        try:
            Verser.objects.all().delete()
            Tampon.objects.all().delete()
            Caisse.objects.all().delete()
            Pret.objects.all().delete()
            Remboursement.objects.all().delete()
            Reunion.objects.all().delete()
            Assist.objects.all().delete()
            Semaine.objects.exclude(pk=1).delete()
            # MontantMbr.objects.all().delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Mot de passe incorrect'}, status=400)

@login_required
def new_week(request):
        try:
            semaine = Semaine.objects.order_by('-pk').first()
            #------ Ajout d'une nouvelle semaine ----
            msg = ''
            now = timezone.now().date() # This will give you a datetime.date object
            
            #dates = [semaine.date_deb.strftime("%d %b %Y"), semaine.date_fin.strftime("%d %b %Y")]
            
            if not (semaine.date_deb <= now <= semaine.date_fin) and now.weekday() <= 5:
                last_monday = now - timedelta(days=now.weekday())
                # Calculate date_fin as 5 days after now
                date_fin = last_monday + timedelta(days=5)

                Semaine.objects.create(
                    date_deb = last_monday,
                    date_fin = date_fin
                )
                new_semaine = Semaine.objects.order_by('-pk').first()
                msg = 'Tafiditra ny herinandro vaovao!\t' + str(new_semaine.date_deb.strftime("%d %b %Y")) + ' à ' + str(new_semaine.date_fin.strftime("%d %b %Y"))  
            else:
                msg = 'Efa ao anatin\'ny herinandro ' + str(semaine.date_deb.strftime("%d %b %Y")) + ' à ' + str(semaine.date_fin.strftime("%d %b %Y")) + ' isika izao!'   
            
            return JsonResponse({'success' : True,'message': msg})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    

@login_required
def reunion_penal(request,pk):
    try:
        assist_record = Assist.objects.get(pk=pk)  # Fetch the record
        assist_record.penalite = False  # Update the penalite field
        assist_record.save()  # Save the changes to the database
        # Assuming `membre` is a ForeignKey to Membre, access the id directly
        membre_instance = assist_record.membre  # This should already be a Membre instance
        msg = 'Voaloa ny sazy 500ar an\'i ' + membre_instance.nom_membre + ' ' + membre_instance.prenom_membre
        # Vérifier s'il y a une caisse active sinon en créer une
        caisses = Caisse.objects.filter(date_fin__gt=timezone.now()).first()
        if not caisses:
            Caisse.objects.create(
                date_deb=timezone.now(),
                date_fin=timezone.now() + timedelta(days=180),
                montant_caisse= 500
            )
        else:
            caisses.montant_caisse += 500
            caisses.save()
        return JsonResponse({'success' : True,'message': msg})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
