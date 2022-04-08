from decimal import Decimal
from django.db.models import Q
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from sweet.pagination import PaginationHandlerMixin, BasicPagination
from sweet.settings import BASE_URL
from .serializer import *
from ..models import *
from ...users.api.trait import imageConvertor
from ...wallets.api.serializer import TransactionSerializer, WithdrawSerializer, TransactionResponse, DepositSerializer
from ...wallets.models import Wallet, Transaction, TransactionType
from mail_templated import send_mail


class MySupplier(APIView):
    def post(self, request):
        if Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are before Registered'}, status.HTTP_400_BAD_REQUEST)
        supplier_serializer = SupplierRegisterSerializer(data=request.data)
        if supplier_serializer.is_valid():
            supplier_serializer.save(user=request.user)
            return Response({'success': True, 'message': 'Register Success', 'data': supplier_serializer.data})
        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': supplier_serializer.errors},
                            status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)
        supplier_serializer = SupplierSerializer(Supplier.objects.get(user=request.user))
        return Response(
            {'success': True, 'message': 'Register Success', 'data': supplier_serializer.data})

    def put(self, request):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)
        supplier = Supplier.objects.get(user=request.user)
        if request.data.get('logo', False):
            if supplier.logo is not None:
                supplier.logo.delete()
            request.data['logo'] = imageConvertor(request.data.pop('logo'))[0]

        if request.data.get('wallpaper', False):
            if supplier.wallpaper is not None:
                supplier.wallpaper.delete()
            request.data['wallpaper'] = imageConvertor(request.data.pop('wallpaper'))[0]

        supplier_serializer = SupplierSerializer(supplier, request.data)
        if supplier_serializer.is_valid():
            supplier_serializer.save(user=request.user)
            return Response(
                {'success': True, 'message': 'Register Success', 'data': supplier_serializer.data})
        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': supplier_serializer.errors},
                            status.HTTP_400_BAD_REQUEST)


@permission_classes((AllowAny,))
class GetBrand(APIView):
    def get(self, request, pk):
        if not Supplier.objects.filter(id=pk).exists():
            return Response({'success': False, 'message': 'Not found'},
                            status.HTTP_404_NOT_FOUND)
        supplier = Supplier.objects.filter(id=pk, state=State.accepted).first()
        brand_serializer = BrandSerializer(supplier)
        product = Product.objects.filter(supplier__id=pk).all()
        return Response(
            {'success': True, 'message': 'mission accomplished', 'data': {'brand': brand_serializer.data, 'products':
                ProductSupplierShowSerializer(product, many=True).data}})


@permission_classes((AllowAny,))
class GetBrandProduct(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def get(self, request, pk):
        product = Product.objects.filter(supplier__id=pk)
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        product = product.filter(and_condition)

        if "sort" in request.GET:
            product = product.order_by(*request.GET['sort'].split(","))

        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                ProductSupplierShowSerializer(self.paginate_queryset(product.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)


@permission_classes((AllowAny,))
class BrandList(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def get(self, request, format=None):
        brand = Supplier.objects.filter()
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        brand = brand.filter(and_condition, state=State.accepted)

        if "sort" in request.GET:
            brand = brand.order_by(*request.GET['sort'].split(","))

        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                BrandSerializer(self.paginate_queryset(brand.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)





@permission_classes((AllowAny,))
class ProductTypeList(APIView):
    def get(self, request):
        type_serializer = ProductTypeSerializer(ProductType.objects.all(), many=True)
        return Response(
            {'success': True, 'message': 'mission accomplished', 'data': type_serializer.data})


@permission_classes((AllowAny,))
class ProductCategoryList(APIView):
    def get(self, request, ):
        return Response({'success': True, 'message': "mission accomplished", 'data': {
            'category': self.getSubCategory(),

        }})

    def getSubCategory(self, ):
        sub_category = Category.objects.all().order_by('id')
        return CategorySerializer(sub_category, many=True).data


@permission_classes((AllowAny,))
class ProductSpecificationList(APIView):
    def get(self, request):
        specification = Specification.objects.all()
        return Response({'success': True, 'message': "mission accomplished", 'data': {
            'specification': SpecificationSerializer(specification, many=True).data,

        }})


class ProductImagesSupplier(APIView):
    def post(self, request):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)
        for item in request.data:
            item['picture'] = imageConvertor(item['picture'])[0]

        images_serializer = ProductImagesCreateSerializer(data=request.data, many=True)
        if images_serializer.is_valid():
            products = [item['product'] for item in request.data]
            users = Product.objects.filter(id__in=products).values_list('supplier__user_id', flat=True)
            if len(set(users)) > 1 or users[0] is not request.user.id:
                return Response({'success': False, 'message': 'Wrong data'}, status.HTTP_403_FORBIDDEN)
            images_serializer.save()
            return Response({'success': True, 'message': 'created', 'data': images_serializer.data})
        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': images_serializer.errors},
                            status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)

        serializers = ProductImagesdeleteSerializer(data=request.data)
        if serializers.is_valid():
            for item in ProductImages.objects.filter(product__supplier__user=request.user,
                                                     id__in=request.data['ids']).all():
                item.picture.delete()
                item.delete()
            return Response({'success': True,
                             'message': "mission accomplished",
                             })
        return Response(
            {'success': False, 'message': 'warning! error occurred',
             'data': {'messages': serializers.errors}},
            status.HTTP_400_BAD_REQUEST)


class ProductSpecificationSupplier(APIView):
    def post(self, request):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)
        specification = ProductSpecificationCreateSerializer(data=request.data, many=True)
        if specification.is_valid():
            products = [item['product'] for item in request.data]
            users = Product.objects.filter(id__in=products).values_list('supplier__user_id', flat=True)
            if len(set(users)) > 1 or users[0] is not request.user.id:
                return Response({'success': False, 'message': 'Wrong data'}, status.HTTP_403_FORBIDDEN)
            ProductSpecification.objects.filter(product__in=products,
                                                product__supplier__user=request.user).delete()
            specification.save()
            return Response({'success': True, 'message': 'created', 'data': specification.data})
        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': specification.errors},
                            status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)

        serializers = ProductSpecificationdeleteSerializer(data=request.data)
        if serializers.is_valid():
            ProductSpecification.objects.filter(product__supplier__user=request.user,
                                                product__in=request.data['ids']).delete()
            return Response({'success': True,
                             'message': "mission accomplished",
                             })
        return Response(
            {'success': False, 'message': 'warning! error occurred',
             'data': {'messages': serializers.errors}},
            status.HTTP_400_BAD_REQUEST)


class ProductDiscountSupplier(APIView):
    def post(self, request):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)
        discount = ProductDiscountSerializer(data=request.data, many=True)
        if discount.is_valid():
            products = [item['product'] for item in request.data]
            users = Product.objects.filter(id__in=products).values_list('supplier__user_id', flat=True)
            if len(set(users)) > 1 or users[0] is not request.user.id:
                return Response({'success': False, 'message': 'Wrong data'}, status.HTTP_403_FORBIDDEN)
            Discount.objects.filter(product__supplier__user=request.user,
                                    product__in=products).delete()
            discount.save()
            return Response({'success': True, 'message': 'created', 'data': discount.data})
        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': discount.errors},
                            status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)

        serializers = ProductDiscountdeleteSerializer(data=request.data)
        if serializers.is_valid():
            Discount.objects.filter(product__supplier__user=request.user,
                                    product__in=request.data['ids']).delete()
            return Response({'success': True,
                             'message': "mission accomplished",
                             })
        return Response(
            {'success': False, 'message': 'warning! error occurred',
             'data': {'messages': serializers.errors}},
            status.HTTP_400_BAD_REQUEST)


class ReplyQuestionSupplier(APIView):
    def put(self, request, pk):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)
        question = QuestionAndAnswer.objects.filter(id=pk, product__supplier__user=request.user).first()
        if question is None:
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)

        question_serializer = QuestionAndAnswerReplySerializer(data=request.data, instance=question)
        if question_serializer.is_valid():
            question_serializer.save(user=request.user)
            # Notification.objects.create(
            #     user=question.user,
            #     notification_description=NotificationDescription.objects.get(
            #         type_of_notification=NotificationType.QUESTION_ANSWER),
            #     link=BASE_URL + '/api/v1/market/product/{}/question?user_id={}'.format(str(question.product.id),
            #                                                                            str(question.user.id))
            # )
            return Response({'success': True, 'message': 'Register Success', 'data': question_serializer.data})
        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': question_serializer.errors},
                            status.HTTP_400_BAD_REQUEST)


class GETProductQuestionSupplier(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def get(self, request, pk):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)
        question = QuestionAndAnswer.objects.filter(product_id=pk, product__supplier__user=request.user)
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        question = question.filter(and_condition)

        if "sort" in request.GET:
            question = question.order_by(*request.GET['sort'].split(","))

        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                QuestionAndAnswerShowSerializer(self.paginate_queryset(question.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)


class GETProductRatingSupplier(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def get(self, request, pk):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)
        rating = Rating.objects.filter(product_id=pk, product__supplier__user=request.user)
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        rating = rating.filter(and_condition)

        if "sort" in request.GET:
            rating = rating.order_by(*request.GET['sort'].split(","))

        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                RatingSerializer(self.paginate_queryset(rating.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)


@permission_classes((AllowAny,))
class GETProduct(APIView):
    def get(self, request, pk):
        product = Product.objects.filter(id=pk).first()
        if request.user.is_authenticated:
            serializer = ProductSupplierDetailSerializer(instance=product, context={'user': request.user.mobile})
        else:
            serializer = ProductSupplierDetailSerializer(instance=product, context={'user': None})
        return Response({'success': True, 'message': 'created', 'data': serializer.data})


class GETProductSupplier(APIView):
    def get(self, request, pk):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)
        product = Product.objects.filter(supplier__user=request.user, id=pk).first()
        return Response({'success': True, 'message': 'created', 'data': ProductSupplierDetailSerializer(product).data})

    def put(self, request, pk):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)
        product = Product.objects.filter(supplier__user=request.user, id=pk).first()
        if product is None:
            return Response({'success': False, 'message': 'You are not before created'},
                            status.HTTP_404_NOT_FOUND)

        if request.data.get('thumbnail', False):
            request.data['thumbnail'] = imageConvertor(request.data.pop('thumbnail'))[0]
        product_serializer = ProductSupplierCreateSerializer(data=request.data, instance=product)
        if product_serializer.is_valid():
            product_serializer.save(supplier=Supplier.objects.get(user=request.user))
            return Response({'success': True, 'message': 'created', 'data': product_serializer.data})

        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': product_serializer.errors},
                            status.HTTP_400_BAD_REQUEST)


class ProductSupplier(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def post(self, request):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)
        # TODO below uuid

        if 'catalog' in request.data:
            if not File.objects.filter(id=request.data['catalog'], user=request.user).exists():
                return Response(
                    {'success': False, 'message': 'wrong make mistake is not ur file',
                     'dev_message': 'Please complete your file',
                     }, status.HTTP_403_FORBIDDEN)
        if 'video' in request.data:
            if not File.objects.filter(id=request.data['video'], user=request.user).exists():
                return Response(
                    {'success': False, 'message': 'wrong make mistake is not ur file',
                     'dev_message': 'Please complete your file',
                     }, status.HTTP_403_FORBIDDEN)

        if request.data.get('thumbnail', False):
            request.data['thumbnail'] = imageConvertor(request.data.pop('thumbnail'))[0]
        product_serializer = ProductSupplierCreateSerializer(data=request.data)
        if product_serializer.is_valid():
            product_serializer.save(supplier=Supplier.objects.get(user=request.user))
            return Response({'success': True, 'message': 'created', 'data': product_serializer.data})

        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': product_serializer.errors},
                            status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        if not Supplier.objects.filter(user=request.user).exists():
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)

        product = Product.objects.filter(supplier__user=request.user)
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        product = product.filter(and_condition)

        if "sort" in request.GET:
            product = product.order_by(*request.GET['sort'].split(","))

        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                ProductSupplierShowSerializer(self.paginate_queryset(product.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)


class OrderStatusList(APIView):
    def enumSerialize(self, enum_class):
        list = []
        for item in range(0, len(enum_class)):
            list.append({
                'id': enum_class(item).value,
                'name': enum_class(item).label
            })
        return list

    def get(self, request):
        return Response(self.enumSerialize(OrderStatus))


class GetProduct(APIView):
    def get(self, request, pk):
        pass


@permission_classes((AllowAny,))
class ProductRating(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def get(self, request, pk):
        rating = Rating.objects.filter(product_id=pk,disable=False)
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        rating = rating.filter(and_condition)

        if "sort" in request.GET:
            rating = rating.order_by(*request.GET['sort'].split(","))

        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                RatingShowSerializer(self.paginate_queryset(rating.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)


class ProductAskQuestion(APIView):
    def post(self, request):
        question_serializer = AskQuestionSerializer(data=request.data)
        if question_serializer.is_valid():
            question = question_serializer.save(user=request.user)
            # Notification.objects.create(
            #     user=question.product.supplier.user,
            #     notification_description=NotificationDescription.objects.get(
            #         type_of_notification=NotificationType.QUESTION),
            #     link=BASE_URL + '/api/v1/market/product/{}/question/supplier'.format(str(question.product.id))
            # )
            return Response({'success': True, 'message': 'Register Success', 'data': question_serializer.data})
        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': question_serializer.errors},
                            status.HTTP_400_BAD_REQUEST)


class AskProductRating(APIView):
    def post(self, request):
        rating_serializer = RatingSerializer(data=request.data)
        if rating_serializer.is_valid():
            rating = rating_serializer.save(user=request.user)
            # Notification.objects.create(
            #     user=rating.product.supplier.user,
            #     notification_description=NotificationDescription.objects.get(
            #         type_of_notification=NotificationType.REVIEW),
            #     link=BASE_URL + '/api/v1/market/product/{}/rating/supplier'.format(str(rating.product.id))
            # )
            return Response({'success': True, 'message': 'Register Success', 'data': rating_serializer.data})
        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': rating_serializer.errors},
                            status.HTTP_400_BAD_REQUEST)


@permission_classes((AllowAny,))
class ProductQuestion(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def get(self, request, pk):
        question = QuestionAndAnswer.objects.filter(product_id=pk,disable=False)
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        question = question.filter(and_condition)

        if "sort" in request.GET:
            question = question.order_by(*request.GET['sort'].split(","))

        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                QuestionAndAnswerShowSerializer(self.paginate_queryset(question.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)


@permission_classes((AllowAny,))
class ProductList(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def get(self, request, format=None):
        product = Product.objects.filter()
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page' or key == 'created_at':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        product = product.filter(and_condition)

        if "sort" in request.GET:
            product = product.order_by(*request.GET['sort'].split(","))

        if 'created_at' in request.GET:
            product = product.filter(created_at__gte=request.GET['created_at'])

        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                ProductSupplierShowSerializer(self.paginate_queryset(product.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)


class ProductFavoriteList(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def get(self, request):
        favorite = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        product = Product.objects.filter(id__in=favorite)
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        product = product.filter(and_condition)

        if "sort" in request.GET:
            product = product.order_by(*request.GET['sort'].split(","))

        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                ProductSupplierShowSerializer(self.paginate_queryset(product.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)

    def post(self, request):
        rating_serializer = FavoriteSerializer(data=request.data)
        if rating_serializer.is_valid():
            if Favorite.objects.filter(user=request.user, product=request.data['product']).exists():
                Favorite.objects.filter(user=request.user, product=request.data['product']).delete()
            else:
                rating_serializer.save(user=request.user)
            return Response({'success': True, 'message': 'Register Success'})
        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': rating_serializer.errors},
                            status.HTTP_400_BAD_REQUEST)


@permission_classes((AllowAny,))
class ProductOffersList(APIView, PaginationHandlerMixin):
    def get(self, request):
        product = Product.objects.filter(extra_discount=True)
        if "sort" in request.GET:
            product = product.order_by(*request.GET['sort'].split(","))

        product = product.order_by('?')[:5]

        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': ProductSupplierShowSerializer(product, many=True).data
        },
            status=status.HTTP_200_OK)


@permission_classes((AllowAny,))
class ProductSliderList(APIView, PaginationHandlerMixin):
    def get(self, request):
        product = Product.objects.filter(slider=True)
        if "sort" in request.GET:
            product = product.order_by(*request.GET['sort'].split(","))

        product = product.order_by('?')[:5]

        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': ProductSupplierShowSerializer(product, many=True).data
        },
            status=status.HTTP_200_OK)


class NotificationList(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def get(self, request):
        notification = Notification.objects.filter(user=request.user)
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        notification = notification.filter(and_condition)

        if "sort" in request.GET:
            notification = notification.order_by(*request.GET['sort'].split(","))
        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                NotificationSerializer(self.paginate_queryset(notification.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)

    def put(self, request):
        if request.user.email == None or request.user.email == "":
            return Response(
                {'success': False, 'message': 'Please complete your profile',
                 'dev_message': 'Please complete your profile',
                 }, status.HTTP_403_FORBIDDEN)
        serializer = UpdateSiteNotificationSerializer(data=request.data)
        if serializer.is_valid():
            Notification.objects.filter(user=request.user, id__in=request.data['ids'], is_read=False).update(
                is_read=True)
            return Response({'success': True,
                             'message': "mission accomplished",
                             'dev_message': 'Read This Notifications'})
        return Response(
            {'success': False, 'message': 'warning! error occurred',
             'data': {'messages': serializer.errors}},
            status.HTTP_400_BAD_REQUEST)


class PurcheaseList(APIView):
    def post(self, request, pk):
        invoice = Invoice.objects.filter(id=pk, order__user=request.user).first()
        if invoice is None:
            return Response({'success': False, 'message': 'You are not before Registered'},
                            status.HTTP_404_NOT_FOUND)
        if invoice.is_purchase:
            return Response({'success': True, 'message': 'You are  before purchase'}, )
        invoice.is_purchase = True
        invoice.save()
        src_wallet = Wallet.objects.get(user=request.user)
        price = invoice.quantity * invoice.price
        if src_wallet.free < price:
            return Response({'success': False, 'message': 'You are not enough money'},
                            status.HTTP_400_BAD_REQUEST)
        src_wallet.free -= Decimal(price)
        src_wallet.save()
        dst_wallet = Wallet.objects.get(user=invoice.product.supplier.user)
        dst_wallet.free += Decimal(price)
        dst_wallet.save()
        # TODO swit
        src_transaction = Transaction(owner=request.user, title="withdraw for purchasing",
                                      description='withdraw for purchasing',
                                      type=TransactionType.WITHDRAW.value, amount=price,
                                      )

        src_transaction.save()
        return Response({'success': True, 'message': 'You are purchasing'}, )


class InvoicePerformaSupplier(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def get(self, request):
        performa = PerforamRequest.objects.filter(invoice__product__supplier__user=request.user)
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        performa = performa.filter(and_condition)

        if "sort" in request.GET:
            performa = performa.order_by(*request.GET['sort'].split(","))
        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                PerforamRequestSerializer(self.paginate_queryset(performa.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)

    def put(self, request):
        performa = PerforamRequest.objects.filter(
            order_id=request.data['order'],
            invoice_id=request.data['invoice'],
            invoice__product__supplier__user=request.user).first()
        if performa == None:
            return Response({'success': False, 'message': 'mistake request'}, status.HTTP_400_BAD_REQUEST)
        is_archive = performa.is_archive
        performa = PerforamRequest.objects.filter(
            order_id=request.data['order'],
            invoice_id=request.data['invoice'],
            invoice__product__supplier__user=request.user).update(is_archive=not is_archive)
        return Response(PerforamRequestSerializer(instance=PerforamRequest.objects.filter(
            order_id=request.data['order'],
            invoice_id=request.data['invoice'],
            invoice__product__supplier__user=request.user).first(), many=False).data)


class InvoicePerformaDetail(APIView):
    def get(self, request, pk):
        performa = PerforamRequest.objects.filter(order__user=request.user, id=pk).first()
        return Response({
            'success': True,
            'message': "mission accomplished",
            'data':
                PerforamRequestSerializer(performa, many=False).data
        },
            status=status.HTTP_200_OK)


class InvoicePerforma(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def post(self, request):
        perforam = PerforamRequestSerializerCreateSerializer(data=request.data, many=False)
        if perforam.is_valid():

            if Invoice.objects.filter(id__in=request.data['invoice'], order__user=request.user).count() != len(
                    request.data['invoice']):
                return Response({'success': False, 'message': 'Wrong data'},
                                status.HTTP_403_FORBIDDEN)
            if PerforamRequest.objects.filter(order=request.data['order'],
                                              invoice__in=request.data['invoice']).count() > 0:
                return Response({'success': True, 'message': 'before created'})
            users = Order.objects.filter(id=request.data['order']).values_list('user', flat=True)
            if len(set(users)) > 1 or users[0] is not request.user.id:
                return Response({'success': False, 'message': 'Wrong data'}, status.HTTP_403_FORBIDDEN)
            perforam.save()
            return Response({'success': True, 'message': 'created', 'data': perforam.data})
        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': perforam.errors},
                            status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        performa = PerforamRequest.objects.filter(order__user=request.user)
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        performa = performa.filter(and_condition)

        if "sort" in request.GET:
            performa = performa.order_by(*request.GET['sort'].split(","))
        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                PerforamRequestSerializer(self.paginate_queryset(performa.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)


class OrderList(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def get(self, request):
        order = Order.objects.filter(user_id=request.user)
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        order = order.filter(and_condition)

        if "sort" in request.GET:
            order = order.order_by(*request.GET['sort'].split(","))

        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                OrderDetailSerializer(self.paginate_queryset(order.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OrderRequestSerializer(data=request.data)
        if serializer.is_valid():
            invoice_serializer = InvoiceRequestCreateSerializer(data=request.data['invoice'], many=True)
            if invoice_serializer.is_valid():
                total_price = 0
                for item in request.data['invoice']:
                    total_discount = 0
                    product = Product.objects.get(id=item['product'])
                    if product.extra_discount:
                        total_discount += product.extra_discount_percent
                    discount = Discount.objects.filter(product_id=item['product'], lower_bound__lte=item['quantity'],
                                                       upper_bound__gte=item['quantity']).first()
                    if discount is not None:
                        total_discount += discount.percent
                    item['price'] = round(product.price * (1 - total_discount / 100), 2)
                    total_price += item['price'] * item['quantity']
                    if not product.unlimited:
                        if product.quantity < item['quantity']:
                            return Response(
                                {'success': False, 'message': 'Wrong data', 'errors': 'quantity product lower than'},
                                status.HTTP_400_BAD_REQUEST)
                        else:
                            product.quantity -= item['quantity']
                            product.save()
                order = serializer.save(total_price=round(total_price, 2), user=request.user)
                """re again serilize becouse change price"""
                invoice_serializer = InvoiceRequestCreateSerializer(data=request.data['invoice'], many=True)
                invoice_serializer.is_valid()
                invoice = invoice_serializer.save(order=order)
                sender = 'sales@toranjestan.com'
                # TODO change receiver baharimahdi and change templat
                # send_mail('mail_templated/{}'.format('rebuild_hourly.html'), {'order': order, 'invoice': invoice},
                #           sender,
                #           ['baharimahdi93@gmail.com'])

                # Notification.objects.create(
                #     user=invoice[0].product.supplier.user,
                #     notification_description=NotificationDescription.objects.get(
                #         type_of_notification=NotificationType.NEW_ORDER),
                #     link=BASE_URL + '/api/v1/market/order/supplier'
                # )
                Transaction.objects.create(
                    owner=request.user,
                    order=order,
                    title='Buy',
                    type= TransactionType.DEPOSIT.value,
                    amount = order.total_price
                )
                return Response({
                    'success': True,
                    'message': "mission accomplished",
                    'data': OrderDetailSerializer(order, many=False).data
                });
            else:
                return Response({'success': False, 'message': 'Wrong data', 'errors': invoice_serializer.errors},
                                status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': serializer.errors},
                            status.HTTP_400_BAD_REQUEST)


class OrderSupplierList(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def get(self, request):
        invoice = Invoice.objects.filter(product__supplier__user=request.user)
        and_condition = Q()
        for key, value in request.GET.items():
            if key == 'sort' or key == 'page' or key == 'is_archive':
                continue
            if ',' in value:
                value = value.split(",")
            and_condition.add(Q(**{key: value}), Q.AND)
        invoice = invoice.filter(and_condition)

        if request.GET.get('is_archive', False):
            invoice = invoice.filter(state=OrderStatus.DELIVERED)

        if "sort" in request.GET:
            invoice = invoice.order_by(*request.GET['sort'].split(","))

        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': self.get_paginated_response(
                InvoiceSupplierSerilizer(self.paginate_queryset(invoice.all()), many=True).data).data
        },
            status=status.HTTP_200_OK)


class OrderSupplierDetailList(APIView):
    def get(self, request, pk):
        invoice = Invoice.objects.filter(id=pk, product__supplier__user=request.user).first()
        return Response({
            'success': True,
            'message': "mission accomplished",
            'data': InvoiceSupplierSerilizer(invoice, many=False).data},
            status=status.HTTP_200_OK)

    def put(self, request, pk):
        serializer = InvoiceStateSerilizer(data=request.data)
        if serializer.is_valid():
            invoice = Invoice.objects.filter(id=pk, product__supplier__user=request.user).first()
            if invoice is None:
                return Response({'success': False, 'message': 'You are not your invoice'},
                                status.HTTP_404_NOT_FOUND)
            invoice.state = request.data['state']
            invoice.save()
            count = Invoice.objects.filter(order_id=invoice.order.id,
                                           state__in=[OrderStatus.ORDER, OrderStatus.PROCESSING,
                                                      OrderStatus.READY_TO_DELIVER,
                                                      ]).count()
            if count == 0:
                invoice.order.is_archive = True
                invoice.order.save()
            else:
                invoice.order.is_archive = False
                invoice.order.save()

            # Notification.objects.create(
            #     user=invoice.order.user,
            #     notification_description=NotificationDescription.objects.get(
            #         type_of_notification=NotificationType.CHANGE_ORDER),
            #     link=BASE_URL + '/api/v1/market/order/' + str(invoice.order.id)
            # )

            return Response({
                'success': True,
                'message': "mission accomplished",
                'data': InvoiceSupplierSerilizer(invoice, many=False).data},
                status=status.HTTP_200_OK)
        # Todo send notification
        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': serializer.errors},
                            status.HTTP_400_BAD_REQUEST)


class GetOrder(APIView):
    def get(self, request, pk):
        order = Order.objects.filter(user_id=request.user, id=pk).first()
        serializer = OrderDetailSerializer(order, many=False)
        return Response({'success': True, 'data': serializer.data, 'message': ''})

@permission_classes((AllowAny,))
class GetOrderQr(APIView):
    def get(self, request, pk):
        order = Order.objects.filter(qr_number=pk).last()
        serializer = OrderDetailSerializer(order, many=False)
        return Response({'success': True, 'data': serializer.data, 'message': ''})


class Deposit(APIView):
    def post(self, request):
        deposit = DepositSerializer(data=request.data)
        if deposit.is_valid():
            wallet = Wallet.objects.filter(user=request.user)
            if wallet.exists():
                new_amount = int(wallet.get().free) + int(request.data['amount'])
                wallet.update(free=new_amount)
                deposit_object = deposit.save(owner=request.user, type=TransactionType.DEPOSIT.value,
                                              title="Deposit in your personal wallet",
                                              description="Deposit in personal wallet from market module", )
                return Response({'success': True, 'data': TransactionResponse(deposit_object, many=False).data,
                                 'message': 'Deposit successfully'})
            else:
                return Response(
                    {'success': False, 'message': 'User dose not have active wallet',
                     'dev_message': 'User dose not have active wallet',
                     }, status.HTTP_403_FORBIDDEN)

        else:
            return Response({'success': False, 'message': 'Wrong data', 'errors': deposit.errors},
                            status.HTTP_400_BAD_REQUEST)


class Withdraw(APIView):
    def post(self, request):
        withdraw = WithdrawSerializer(data=request.data)
        if withdraw.is_valid():
            wallet = Wallet.objects.filter(user=request.user)
            if wallet.exists():
                if int(wallet.get().free) > int(request.data['amount']):
                    new_amount = int(wallet.get().free) - int(request.data['amount'])
                    wallet.update(free=new_amount)
                    deposit_object = withdraw.save(owner=request.user, type=TransactionType.WITHDRAW.value,
                                                   title="Withdraw from your personal wallet",
                                                   description="Withdraw from your personal wallet from wallet", )
                    return Response({'success': True, 'data': TransactionResponse(deposit_object, many=False).data,
                                     'message': 'Deposit successfully'})
                else:
                    return Response(
                        {'success': False, 'message': 'Wallet balance is not enough',
                         'dev_message': 'Wallet balance is not enough',
                         }, status.HTTP_403_FORBIDDEN)

            else:
                return Response(
                    {'success': False, 'message': 'User dose not have active wallet',
                     'dev_message': 'User dose not have active wallet',
                     }, status.HTTP_403_FORBIDDEN)


class TransactionList(APIView):
    def get(self, request):
        trans = Transaction.objects.filter(owner=request.user)
        serializer = TransactionSerializer(trans, many=True)
        return Response(
            {'success': True, 'data': serializer.data, 'message': 'Project Transaction list load successfully'})
