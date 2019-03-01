from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, mixins, status,
                            viewsets)
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from stores.models import Store, Product
from stores.permissions import IsOwnerStores, IsOwnerProducts
from stores.serializers import StoreSerializer, NonAuthenticatedGetProduct, ActivatePlanSerializer, ProductSerializer, \
    SyncSerializer
from vfrlight.util import get_or_raise


class StoreViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsOwnerStores,)
    serializer_class = StoreSerializer
    queryset = Store.objects.all()
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        try:
            store = Store.objects.get(slug=self.kwargs['slug'])
        except:
            raise NotFound(
                detail="store {} not found".format(self.kwargs['slug']))
        if not (store.owner.user == self.request.user):
            raise PermissionDenied
        return Response(StoreSerializer(store).data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # refresh the instance from the database.
            instance = self.get_object()
            serializer = self.get_serializer(instance)

        return Response(serializer.data)


class NonAuthenticatedGetProductViewSet(viewsets.ViewSet):
    """
        it's used in the store front when we want to get the gender,
        covered by the plan and is ready to try, since we dont have any credentials
        there we allow only get request
    """
    http_method_names = ['get', 'options']
    serializer_class = NonAuthenticatedGetProduct
    queryset = []

    def retrieve(self, *args, **kwargs):

        serializer = self.serializer_class(data=kwargs)
        if serializer.is_valid(raise_exception=ValueError):
            product = Product.objects.get(
                shopify_id=serializer.data['pk'])
            return Response(ProductSerializer(product).data,
                            status=status.HTTP_302_FOUND)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ModelViewSet):
    authentication_classes = (
        JSONWebTokenAuthentication,)
    permission_classes = (IsOwnerProducts,)
    http_method_names = ['get', 'put', 'option']
    filter_fields = ('gender', 'product_type', 'fit_type',)

    # this will match the whole title, replace it with title__icontains
    # search_fields = ('=title',)

    serializer_class = ProductSerializer
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('title', 'updated_at', 'created_at')

    # queryset = Product.objects.all()

    def get_queryset(self):
        store = get_or_raise(Store, slug=self.kwargs['store_slug'])
        if not (store.owner.user == self.request.user):
            raise PermissionDenied
        queryset = Product.objects.filter(store=store)
        if 'search' in self.request.query_params and self.request.query_params['search']:
            queryset = queryset.filter(
                title__icontains=self.request.query_params['search'])
        if ('ready_to_try' in self.request.query_params and
                self.request.query_params['ready_to_try']):
            def str2bool(v):
                return v.lower() in ("yes", "true", "t", "1")

            pk_list = [x.shopify_id for x in queryset
                       if x.ready_to_try == str2bool(self.request.query_params['ready_to_try'])]
            queryset = Product.objects.filter(shopify_id__in=pk_list)

        return queryset


class SyncViewSet(viewsets.ViewSet):
    """
        empty post request, with authentication header, to sync store's data
    """
    http_method_names = ['post', 'options']
    serializer_class = SyncSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsOwnerStores,)

    def create(self, request, *args, **kwargs):
        try:
            # store = Store.objects.get(slug=kwargs['store_slug'])
            store = Store.objects.get(slug=kwargs['store_slug'])

        except:
            raise NotFound(
                detail="store {} not found".format(kwargs['store_slug']))
        if not (store.owner.user == self.request.user):
            raise PermissionDenied
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            data = serializer.create(
                validated_data=serializer.data, store=store)
            return Response(data,
                            status=status.HTTP_200_OK)
        return Response(serializer.error_messages,
                        status=status.HTTP_400_BAD_REQUEST)


class ActivatePlanViewSet(viewsets.ViewSet):
    """
        {
            'plan' = 'Male'
        }
        plan values could be ['Male', 'Female', 'MaleAndFemale']
        Errors: if plan is activated, `you are already activated the plan`


        AFTER admin confirm on the charge the response will be
        {"data": "plan:Male with status:activated"}
    """
    http_method_names = ['post', 'options']
    serializer_class = ActivatePlanSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsOwnerStores,)

    def create(self, request, *args, **kwargs):
        try:
            store = Store.objects.get(slug=kwargs['store_slug'])
        except:
            raise NotFound(
                detail="store {} not found".format(kwargs['store_slug']))
        if not (store.owner.user == self.request.user):
            raise PermissionDenied
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            plan = serializer.data['plan']
            if len(plan.split(" ")) == 1:
                plan = plan + " Second"
            if store.plans[plan]:
                return Response({"error": "you are already activated the plan"},
                                status=status.HTTP_200_OK)
            else:
                confirmation = serializer.create(
                    validated_data=serializer.data, store=store)
                if confirmation:
                    return Response({'url_confirmation': confirmation},
                                    status=status.HTTP_200_OK)
        return Response(serializer.error_messages,
                        status=status.HTTP_400_BAD_REQUEST)
