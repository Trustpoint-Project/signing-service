"""Contains all the views of Signer App."""

import base64
import json

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import SignerForm
from .models import SignedMessage, Signer
from .utils.keygen import generate_private_key, load_private_key_object

# def signer_list(request: HttpRequest) -> HttpResponse:
#     """Renders HTML page for Signer List."""
#     signers = Signer.objects.all()
#     return render(request, 'signerlist.html', {'signers': signers})


class SignerList(ListView):
    model = Signer
    paginate_by = 10
    template_name = 'signerlist.html'
    context_object_name = 'signers'
    ordering = ['-created_on']


# @require_POST
# def delete_signer(request: HttpRequest, signer_id: int) -> HttpResponse:
#     """Rerenders HTML page when Signer is Delete."""
#     signer = get_object_or_404(Signer, pk=signer_id)
#     signer.delete()
#     return redirect('signerList')


class SignerDelete(DeleteView):
    model = Signer
    paginate_by = 10
    success_url = reverse_lazy('signerList')


class SignerEdit(UpdateView):
    model = Signer
    success_url = reverse_lazy('signerList')
    form_class = SignerForm
    template_name = 'addSigner.html'
    context_object_name = 'signer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Edit Signer'
        return context

    def form_valid(self, form):
        signer = form.save(commit=False)

        signer.private_key = generate_private_key(
            algorithm_oid_str=signer.signing_algorithm,
            curve_name=signer.curve,
            key_size=signer.key_length,
        )

        private_key_obj = load_private_key_object(signer.private_key)
        public_key = private_key_obj.public_key()

        # Create self-signed certificate
        builder = (
            x509.CertificateBuilder()
            .subject_name(
                x509.Name(
                    [
                        x509.NameAttribute(x509.NameOID.COMMON_NAME, signer.unique_name),
                    ]
                )
            )
            .issuer_name(
                x509.Name(
                    [
                        x509.NameAttribute(x509.NameOID.COMMON_NAME, signer.unique_name),
                    ]
                )
            )
            .public_key(public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(timezone.now())
            .not_valid_after(signer.expires_by)
        )

        certificate = builder.sign(private_key=private_key_obj, algorithm=hashes.SHA256())

        signer.certificate = certificate.public_bytes(serialization.Encoding.PEM).decode()

        signer.save()
        return redirect(self.success_url)


# def edit_signer(request: HttpRequest, signer_id: int) -> HttpResponse:
#     signer = get_object_or_404(Signer, pk=signer_id)
#
#     if request.method == 'POST':
#         form = SignerForm(request.POST, instance=signer)
#         if form.is_valid():
#             form.save()
#             return redirect('signerList')
#     else:
#         form = SignerForm(instance=signer)
#
#     signing_algorithm_choices = [
#         (alg.dotted_string, alg.verbose_name) for alg in AlgorithmIdentifier if alg.hash_algorithm is not None
#     ]
#     algo_hash_map = {
#         alg.dotted_string: alg.hash_algorithm.verbose_name
#         for alg in AlgorithmIdentifier
#         if alg.hash_algorithm is not None
#     }
#     ecc_curves = [
#         (curve.value.ossl_curve_name, curve.value.verbose_name)
#         for curve in NamedCurve
#         if curve.value.curve is not None and curve.name != 'NONE'
#     ]
#
#     return render(
#         request,
#         'addSigner.html',
#         {
#             'form': form,
#             'signing_algorithms': signing_algorithm_choices,
#             'algo_hash_map_json': json.dumps(algo_hash_map),
#             'ecc_curves': ecc_curves,
#         },
#     )
#


class SignerDetail(DetailView):
    model = Signer
    paginate_by = 10
    template_name = 'signer_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        signer = self.get_object()

        # Load signed messages
        context['signed_messages'] = signer.signed_messages.all()

        # Load certificate details
        try:
            cert_obj = x509.load_pem_x509_certificate(signer.certificate.encode())
            context['cert_details'] = {
                'subject': cert_obj.subject.rfc4514_string(),
                'issuer': cert_obj.issuer.rfc4514_string(),
                'serial_number': cert_obj.serial_number,
                'not_valid_before': cert_obj.not_valid_before,
                'not_valid_after': cert_obj.not_valid_after,
                'certificate': cert_obj.public_bytes(encoding=serialization.Encoding.PEM).decode('utf-8'),
            }
        except Exception as e:
            context['cert_details'] = {'error': f'Certificate could not be parsed: {e}'}

        return context


# def signer_detail(request: HttpRequest, signer_id: int) -> HttpResponse:
#     """Renders detail view of a single signer."""
#     signer = get_object_or_404(Signer, pk=signer_id)
#     signed_msgs = SignedMessage.objects.filter(signer=signer)
#     cert_details = None
#     try:
#         cert_obj = x509.load_pem_x509_certificate(signer.certificate.encode())
#         cert_details = {
#             'subject': cert_obj.subject.rfc4514_string(),
#             'issuer': cert_obj.issuer.rfc4514_string(),
#             'serial_number': cert_obj.serial_number,
#             'not_valid_before': cert_obj.not_valid_before,
#             'not_valid_after': cert_obj.not_valid_after,
#             'public_key': cert_obj.public_key()
#             .public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
#             .decode('utf-8'),
#             'certificate': signer.certificate,
#         }
#     except Exception as e:
#         cert_details = {'error': f'Certificate could not be parsed: {e}'}
#
#     return render(
#         request,
#         'signer_detail.html',
#         {
#             'signer': signer,
#             'signed_messages': signed_msgs,
#             'cert_details': cert_details,
#         },
#     )


class SignerCreate(CreateView):
    model = Signer
    form_class = SignerForm
    template_name = 'addSigner.html'
    success_url = reverse_lazy('signerList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add Signer'
        return context

    def form_valid(self, form):
        signer = form.save(commit=False)

        signer.private_key = generate_private_key(
            algorithm_oid_str=signer.signing_algorithm,
            curve_name=signer.curve,
            key_size=signer.key_length,
        )

        private_key_obj = load_private_key_object(signer.private_key)
        public_key = private_key_obj.public_key()

        # Create self-signed certificate
        builder = (
            x509.CertificateBuilder()
            .subject_name(
                x509.Name(
                    [
                        x509.NameAttribute(x509.NameOID.COMMON_NAME, signer.unique_name),
                    ]
                )
            )
            .issuer_name(
                x509.Name(
                    [
                        x509.NameAttribute(x509.NameOID.COMMON_NAME, signer.unique_name),
                    ]
                )
            )
            .public_key(public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(timezone.now())
            .not_valid_after(signer.expires_by)
        )

        certificate = builder.sign(private_key=private_key_obj, algorithm=hashes.SHA256())

        signer.certificate = certificate.public_bytes(serialization.Encoding.PEM).decode()

        signer.save()
        return redirect(self.success_url)


# def add_signer(request: HttpRequest) -> HttpResponse:
#     """Renders HTML page for Adding a Signer."""
#     signing_algorithm_choices = [
#         (alg.dotted_string, alg.verbose_name) for alg in AlgorithmIdentifier if alg.hash_algorithm is not None
#     ]
#
#     algo_hash_map = {
#         alg.dotted_string: alg.hash_algorithm.verbose_name
#         for alg in AlgorithmIdentifier
#         if alg.hash_algorithm is not None
#     }
#     ecc_curves = [
#         (curve.value.ossl_curve_name, curve.value.verbose_name)
#         for curve in NamedCurve
#         if curve.value.curve is not None and curve.name != 'NONE'
#     ]
#
#     if request.method == 'POST':
#         print('Post Accessed')
#         form = SignerForm(request.POST)
#         if form.is_valid():
#             signer = form.save(commit=False)
#
#             signer.private_key = generate_private_key(
#                 algorithm_oid_str=signer.signing_algorithm, curve_name=signer.curve, key_size=signer.key_length
#             )
#
#             private_key_obj = load_private_key_object(signer.private_key)
#             public_key = private_key_obj.public_key()
#
#             # self-signed cert
#             builder = (
#                 x509.CertificateBuilder()
#                 .subject_name(
#                     x509.Name(
#                         [
#                             x509.NameAttribute(x509.NameOID.COMMON_NAME, signer.unique_name),
#                         ]
#                     )
#                 )
#                 .issuer_name(
#                     x509.Name(
#                         [
#                             x509.NameAttribute(x509.NameOID.COMMON_NAME, signer.unique_name),
#                         ]
#                     )
#                 )
#                 .public_key(public_key)
#                 .serial_number(x509.random_serial_number())
#                 .not_valid_before(timezone.now())
#                 .not_valid_after(signer.expires_by)
#             )
#
#             certificate = builder.sign(private_key=private_key_obj, algorithm=hashes.SHA256())
#
#             signer.certificate = certificate.public_bytes(serialization.Encoding.PEM).decode()
#
#             signer.save()
#             return redirect('signerList')
#     else:
#         form = SignerForm()
#
#     cast('ChoiceField', form.fields['signing_algorithm']).choices = signing_algorithm_choices
#
#     return render(
#         request,
#         'addSigner1.html',
#         {
#             'form': form,
#             'signing_algorithms': signing_algorithm_choices,
#             'algo_hash_map_json': json.dumps(algo_hash_map),
#             'ecc_curves': ecc_curves,
#         },
#     )


@method_decorator(csrf_exempt, name='dispatch')
class SignHashAPIView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            signer_id = data.get('signer_id')
            hash_hex = data.get('hash')

            if not signer_id or not hash_hex:
                return JsonResponse({'error': 'Missing signer_id or hash'}, status=400)

            signer = Signer.objects.get(pk=signer_id)
            private_key = load_private_key_object(signer.private_key)
            hash_bytes = bytes.fromhex(hash_hex)

            if signer.signing_algorithm.startswith('1.2.840.113549.1.1.'):  # RSA
                signature = private_key.sign(hash_bytes, padding.PKCS1v15(), getattr(hashes, signer.hash_function)())
            elif signer.signing_algorithm.startswith('1.2.840.10045.4.'):  # ECC
                signature = private_key.sign(hash_bytes, ec.ECDSA(getattr(hashes, signer.hash_function)()))
            else:
                return JsonResponse({'error': 'Unsupported algorithm'}, status=400)

            SignedMessage.objects.create(
                signer=signer, hash_value=hash_hex, signature=base64.b64encode(signature).decode()
            )

            return JsonResponse({'signature': base64.b64encode(signature).decode()}, status=200)

        except Signer.DoesNotExist:
            return JsonResponse({'error': 'Signer not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# @csrf_exempt
# def sign_hash_api(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Only POST allowed'}, status=405)
#
#     try:
#         data = json.loads(request.body)
#         signer_id = data.get('signer_id')
#         hash_hex = data.get('hash')
#         if not signer_id or not hash_hex:
#             return JsonResponse({'error': 'Missing signer_id or hash'}, status=400)
#
#         signer = Signer.objects.get(pk=signer_id)
#         private_key = load_private_key_object(signer.private_key)
#
#         hash_bytes = bytes.fromhex(hash_hex)
#
#         if signer.signing_algorithm.startswith('1.2.840.113549.1.1.'):  # Check if its RSA
#             signature = private_key.sign(hash_bytes, padding.PKCS1v15(), getattr(hashes, signer.hash_function)())
#         elif signer.signing_algorithm.startswith('1.2.840.10045.4.'):  # Checks for ECC
#             signature = private_key.sign(hash_bytes, ec.ECDSA(getattr(hashes, signer.hash_function)()))
#         else:
#             return JsonResponse({'error': 'Unsupported algorithm'}, status=400)
#         from .models import SignedMessage
#
#         SignedMessage.objects.create(signer=signer, hash_value=hash_hex, signature=base64.b64encode(signature).decode())
#         return JsonResponse({'signature': base64.b64encode(signature).decode()}, status=200)
#
#     except Signer.DoesNotExist:
#         return JsonResponse({'error': 'Signer not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
