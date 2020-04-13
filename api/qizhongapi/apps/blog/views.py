from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import ListAPIView
from utils.response import APIResponse
from . import models, serializers, throttles
from django.core.cache import cache
from rest_framework.response import Response
import re
from django.conf import settings
from libs import tx_sms
from django.db.models import Count
import json


# Create your views here.
class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        print(985)
        print(request.data.get('username'))
        print(request.data.get('password'))
        serializer = serializers.LoginModelSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer.user.nickname)

            return APIResponse(data={
                'username': serializer.user.username,
                'id': serializer.user.id,
                'nickname': serializer.user.nickname,
                'token': serializer.token
            })
        return APIResponse(1, 'failed', data=serializer.errors, http_status=400)


class LoginMobileAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = serializers.LoginMobileSerializer(data=request.data)
        if serializer.is_valid():
            return APIResponse(data={
                'username': serializer.user.username,
                'id': serializer.user.id,
                'nickname': serializer.user.nickname,
                'token': serializer.token
            })
        return APIResponse(1, 'failed', data=serializer.errors, http_status=400)


class RegisterAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        avatar_obj = request.data.get('avatar')
        if not avatar_obj:
            serializer = serializers.RegistersMobileSerializer(data=request.data)
            if serializer.is_valid():
                obj = serializer.save()
                models.UserDetails.objects.create(user_id=obj.id)
                return APIResponse(0, '注册成功', data={
                    'username': obj.username,
                    'id': obj.id,
                    'nickname': obj.nickname,
                    'phone': obj.phone,
                })
            print(456)
            return APIResponse(1, '注册失败', data=serializer.errors, http_status=400)

        serializer = serializers.RegisterMobileSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            models.UserDetails.objects.create(user_id=obj.id)
            return APIResponse(0, '注册成功', data={
                'username': obj.username,
                'id': obj.id,
                'nickname': obj.nickname,
                'phone': obj.phone,
            })
        return APIResponse(1, '注册失败', data=serializer.errors, http_status=400)


class SMSAPIView(APIView):
    throttle_classes = [throttles.SMSRateThrottle]

    def post(self, request, *args, **kwargs):
        # 拿到前台手机
        print(12)
        phone = request.data.get('phone')
        if not (phone and re.match(r'^1[3-9][0-9]{9}$', phone)):
            return APIResponse(2, '手机号格式有误')
        # 获取验证码
        print(phone)
        code = tx_sms.get_code()
        print(45, code)
        # 发送短信
        print(12, settings.SMS_EXP)

        result = tx_sms.send_sms(phone, code, settings.SMS_EXP // 60)

        # 服务器缓存验证码
        print(49, result)
        if not result:
            return APIResponse(1, '发送验证码失败')
        cache.set(settings.SMS_CACHE_KEY % phone, code, settings.SMS_EXP)
        # 校验发送的验证码与缓存的验证码是否一致
        # print('>>>> %s - %s <<<<' % (code, cache.get('sms_%s' % mobile)))
        return APIResponse(0, '发送验证码成功')


class MobileAPIView(APIView):
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        print(12, settings.SMS_EXP)

        # 不管前台处不处理格式校验，后台一定需要校验
        if not (phone and re.match(r'^1[3-9][0-9]{9}$', phone)):
            return APIResponse(2, '手机号格式有误', http_status=400)

        try:
            # 已经注册了
            models.UserInfo.objects.get(phone=phone)
            return APIResponse(1, '手机已注册')
        except:
            # 没有注册过
            return APIResponse(0, '手机未注册')


class EmailAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        print(email)
        # 不管前台处不处理格式校验，后台一定需要校验
        if not (email and re.match(r'.*@.*', email)):
            return APIResponse(2, '邮箱格式有误', http_status=400)

        try:
            # 已经注册了
            models.UserInfo.objects.get(email=email)
            return APIResponse(1, '邮箱已注册')
        except:
            # 没有注册过
            return APIResponse(0, '邮箱未注册')


class AvatarListAPIView(APIView):
    # queryset = models.UserInfo.objects.filter(is_delete=False, is_show=True).order_by('-order')[:settings.BANNER_COUNT]

    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        print(985)
        try:
            print(request.data.get('username'))

            serializer = serializers.AvatarModelSerializer(data=request.data)
            if serializer.is_valid():
                print(serializer.user.nickname)
                print(serializer.user.avatar)

                return APIResponse(0, 'success', data={

                    'avatar': f"http://127.0.0.1:8040/media/{serializer.user.avatar}",
                    'nickname': serializer.user.nickname,

                })
            return APIResponse(1, 'failed', data=serializer.errors, http_status=400)
        except:
            return APIResponse(1, '错误', http_status=400)


class UserdetailsAPIView(APIView):
    # queryset = models.UserInfo.objects.filter(is_delete=False, is_show=True).order_by('-order')[:settings.BANNER_COUNT]

    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        print(985)
        try:

            serializer = serializers.AdvertisingModelSerializer(data=request.data)
            if serializer.is_valid():
                return APIResponse(0, 'success', data={
                    'advertising': f"http://127.0.0.1:8040/media/{serializer.userdetail.advertising}",
                    'details': serializer.userdetail.details,
                    'introduce': serializer.userdetail.introduce,
                })
            return APIResponse(1, 'failed', data=serializer.errors, http_status=400)
        except:
            return APIResponse(1, '错误', http_status=400)


class InformationsAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:

            username = request.data.get('username')
            user = models.UserInfo.objects.filter(username=username).first()
            print(12)
            userdetail = user.userdetails
            advertising_obj = request.data.get('advertising')
            if not advertising_obj:
                serializer = serializers.InterMobilessSerializer(data=request.data, instance=userdetail)
                print(169)
                if serializer.is_valid():
                    print(1445)
                    print(serializers)
                    obj = serializer.save()
                    return APIResponse(0, '完善成功')
                print(456)
                return APIResponse(1, '完善失败', data=serializer.errors, http_status=400)
            serializer = serializers.InterMobileSerializer(data=request.data, instance=userdetail)
            print(169)
            if serializer.is_valid():
                print(1445)
                print(serializers)
                obj = serializer.save()
                return APIResponse(0, '完善成功')
            print(456)
            return APIResponse(1, '完善失败', data=serializer.errors, http_status=400)
        except:
            return APIResponse(1, '错误', http_status=400)


class CategoryAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            print(request.data)
            username = request.data.get('username')
            user = models.UserInfo.objects.filter(username=username).first()
            blogs = user.blogs
            print(45)
            serializer = serializers.CategoryMobileSerializer(data=request.data)
            if serializer.is_valid():
                print(serializers)
                print(user)
                obj = serializer.save()
                print(obj)
                obj.blog = blogs
                obj.save()
                return APIResponse(0, '完善成功')
            return APIResponse(1, '完善失败', data=serializer.errors, http_status=400)
        except:
            return APIResponse(1, '错误', http_status=400)


class PictureAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            print(request.data)
            s = request.data.get('picture')
            print(s)
            serializer = serializers.PictureMobileSerializer(data=request.data)
            if serializer.is_valid():
                print(14, serializer)

                obj = serializer.save()
                print(56, obj.picture)
                return APIResponse(0, 'success', data={

                    'picture': f"http://127.0.0.1:8040/media/{obj.picture}",

                })
            return APIResponse(1, '完善失败', data=serializer.errors, http_status=400)
        except:
            return APIResponse(1, '错误', http_status=400)


class TagAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            print(request.data)
            username = request.data.get('username')
            user = models.UserInfo.objects.filter(username=username).first()
            blogs = user.blogs
            print(45)
            serializer = serializers.TagMobileSerializer(data=request.data)
            if serializer.is_valid():
                print(serializers)
                print(user)
                obj = serializer.save()
                print(obj)
                obj.blog = blogs
                obj.save()
                return APIResponse(0, '完善成功')
            return APIResponse(1, '完善失败', data=serializer.errors, http_status=400)
        except:
            return APIResponse(1, '错误', http_status=400)


class ChangeinformationAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        print(request.data)
        username = request.data.get('username')
        password = request.data.get('password')
        user = models.UserInfo.objects.filter(username=username).first()
        print(12)
        advertising_obj = request.data.get('avatar')
        print(advertising_obj)
        if not advertising_obj:
            print(45)
            serializer = serializers.ChangeinformationMobileSerializer(data=request.data, instance=user)
            if serializer.is_valid():
                print(serializers)
                obj = serializer.save()
                obj.set_password(password)
                obj.save()
                return APIResponse(0, '修改成功')
            return APIResponse(1, '修改失败', data=serializer.errors, http_status=400)
        serializer = serializers.ChangeinformationsMobileSerializer(data=request.data, instance=user)
        print(169)
        if serializer.is_valid():
            print(1445)
            print(serializers)
            obj = serializer.save()
            obj.set_password(password)
            obj.save()
            return APIResponse(0, '修改成功')
        print(456)
        return APIResponse(1, '修改失败', data=serializer.errors, http_status=400)


class ArticlesAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:

            username = request.data.get('username')
            print(12, username)
            user = models.UserInfo.objects.filter(id=username).first()
            blog = user.blogs
            print(blog)
            article = models.Article.objects.filter(blogs=blog)

            serializerss = serializers.ArticleModelSerializer(instance=article, many=True)
            print(66,serializerss.data)
            # pagination_class = CoursePageNumberPagination

            return Response(serializerss.data)

        except:
            return APIResponse(1, '错误', http_status=400)


class ArtlistAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:

            username = request.data.get('username')
            print(12, username)
            user = models.UserInfo.objects.filter(id=username).first()
            blog = user.blogs
            print(blog)
            article = models.Article.objects.filter(blogs=blog).order_by('-create_time')
            print(article)

            serializerss = serializers.ArticleModelSerializer(instance=article, many=True)
            print(981,serializerss.data)
            # pagination_class = CoursePageNumberPagination

            return Response(serializerss.data)

        except:
            return APIResponse(1, '错误', http_status=400)


class ClassarticleAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            category = request.data.get('category')
            print(category)
            article = models.Article.objects.filter(category=category)

            serializerss = serializers.ArticleModelSerializer(instance=article, many=True)

            print(12, serializerss.data)
            return Response(serializerss.data)
        except:
            return APIResponse(1, '错误', http_status=400)


class CategorysAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')

            user = models.UserInfo.objects.filter(username=username).first()
            blog = user.blogs
            category = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
                'name', 'count_num', 'pk')
            print(category)
            # serializerss = serializers.CategorysModelSerializer(instance=category, many=True)
            # print(serializerss.data)
            return Response(category)
        except:
            return APIResponse(1, '错误', http_status=400)


class CategoryssAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')

            user = models.UserInfo.objects.filter(username=username).first()
            blog = user.blogs
            category = models.Category.objects.filter(blog=blog)
            #     print(category)
            serializerss = serializers.CategorysModelSerializer(instance=category, many=True)
            print(serializerss.data)
            return Response(serializerss.data)
        except:
            return APIResponse(1, '错误', http_status=400)


class CategorylistAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            category = request.data.get('category')
            print(category)

            article = models.Article.objects.filter(category=category)
            print(article)
            serializerss = serializers.ArticlesModelSerializer(instance=article, many=True)
            print(serializerss.data)
            return Response(serializerss.data)
        except:
            return APIResponse(1, '错误', http_status=400)


class ArticleslistAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):

        try:
            article_list = cache.get('article_list')
            if not article_list:
                article = models.Article.objects.all()
                print(article)
                for i in article:
                    print(i.blogs.userinfo.nickname)
                    i.nickname = i.blogs.userinfo.nickname
                    i.user_id = i.blogs.userinfo.id
                serializerss = serializers.ArticleslistModelSerializer(instance=article, many=True)
                print(serializerss.data)
                cache.set('article_list', serializerss.data, 10)
                return Response(serializerss.data)
            return Response(article_list)
        except:
            return APIResponse(1, '错误', http_status=400)


class QueryAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):

        try:
            article_list = []
            input = request.data.get('input')
            article = models.Article.objects.all()
            print(article)
            for i in article:
                print(i.blogs.userinfo.nickname)
                i.nickname = i.blogs.userinfo.nickname
                i.user_id = i.blogs.userinfo.id
            for l in article:
                if input in l.title or input in l.intro:
                    article_list.append(l)

            serializerss = serializers.ArticleslistModelSerializer(instance=article_list, many=True)
            print(serializerss.data)
            return Response(serializerss.data)

        except:
            return APIResponse(1, '错误', http_status=400)


class ArticlelistAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:

            tag = request.data.get("tag")
            print(tag)
            artice_lists = []
            article = models.Article2Tag.objects.filter(tag=tag)
            print(article)
            for l in article:
                print(l.article)
                artice_lists.append(l.article)

            for i in artice_lists:
                print(i.blogs.userinfo.nickname)
                i.nickname = i.blogs.userinfo.nickname
                i.user_id = i.blogs.userinfo.id
            serializerss = serializers.ArticleslistModelSerializer(instance=artice_lists, many=True)
            print(serializerss.data)
            return Response(serializerss.data)
        except:
            return APIResponse(1, '错误', http_status=400)


class TagsAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:

            tag = models.Tag.objects.all()
            print(tag)
            serializerss = serializers.TagMobileSerializer(instance=tag, many=True)

            print(serializerss.data)
            return Response(serializerss.data)
        except:
            return APIResponse(1, '错误', http_status=400)


class ArticleAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            id = request.data.get('id')
            article = models.Article.objects.filter(id=id).first()

            serializerss = serializers.ArticlesModelSerializer(instance=article)
            print(serializerss.data)
            return Response(serializerss.data)
        except:
            return APIResponse(1, '错误', http_status=400)


class CommentAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            user = request.data.get('user')
            article = request.data.get('article')
            parent = request.data.get('parent')
            user = models.UserInfo.objects.filter(id=user).first()
            article = models.Article.objects.filter(id=article).first()
            if not parent:
                serializerss = serializers.CommentModelSerializer(data=request.data)
                if serializerss.is_valid():
                    obj = serializerss.save()
                    obj.user = user
                    obj.article = article
                    obj.save()
                    return APIResponse(0, '修改成功')
                return APIResponse(1, '修改失败')
            print(parent)
            parent = models.Comment.objects.filter(id=parent).first()
            print(parent)
            serializerss = serializers.CommentModelSerializer(data=request.data)
            if serializerss.is_valid():
                obj = serializerss.save()
                obj.user = user
                print(528, obj.user)
                obj.article = article
                print(528, obj.article)
                obj.parent = parent
                print(528, obj.parent)
                obj.save()

                return APIResponse(0, '修改成功')
            return APIResponse(1, '修改失败')
        except:
            return APIResponse(1, '错误', http_status=400)


class Comment_listAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            article_id = request.data.get('article_id')
            print(article_id)

            article = models.Comment.objects.filter(article=article_id).all()
            for i in article:
                print(124, i.user.nickname)
                i.nickname = i.user.nickname
                i.user_id = i.user.id
                i.avatar = i.user.avatar
                if i.parent:
                    i.parent_name = i.parent.user.nickname
                    print(36, i.parent_name)
                elif not i.parent:
                    i.parent_name = ''
                    print(38, i.parent_name)
            serializerss = serializers.Comment_listsModelSerializer(instance=article, many=True)
            print(serializerss.data)
            return Response(serializerss.data)
        except:
            return APIResponse(1, '错误', http_status=400)


class BackgroundAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            print(request.data)
            username = request.data.get('username')
            category = request.data.get('category')
            tag = request.data.get('tag')
            user = models.UserInfo.objects.filter(username=username).first()
            blog = user.blogs
            category = models.Category.objects.filter(id=category).first()
            tag = models.Tag.objects.filter(id=tag).first()
            picture = request.data.get('picture')
            print(45)
            if not picture:
                serializer = serializers.BackgroundsMobileSerializer(data=request.data)
                if serializer.is_valid():
                    print(serializers)
                    obj = serializer.save()
                    print(obj)
                    obj.blogs = blog
                    obj.category = category
                    obj.save()
                    models.Article2Tag.objects.create(article=obj, tag=tag)
                    return APIResponse(0, '完善成功')
                return APIResponse(1, '完善失败', data=serializer.errors, http_status=400)
            serializer = serializers.BackgroundMobileSerializer(data=request.data)
            if serializer.is_valid():
                print(serializers)
                obj = serializer.save()
                print(obj)
                obj.blogs = blog
                obj.category = category
                obj.save()
                models.Article2Tag.objects.create(article=obj, tag=tag)
                return APIResponse(0, '完善成功')
            return APIResponse(1, '完善失败', data=serializer.errors, http_status=400)
        except:
            return APIResponse(1, '错误', http_status=400)
