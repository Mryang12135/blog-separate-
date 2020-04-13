import re

from rest_framework import serializers
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from django.core.cache import cache
from django.conf import settings

from . import models



# 多方式登录
class LoginModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = models.UserInfo
        fields = ('username', 'password')

    # 校验user，签发token，保存到serializer
    # 那种drf-jwt
    def validate(self, attrs):
        # user = authenticate(**attrs)
        # 账号密码登录 => 多方式登录
        user = self._many_method_login(**attrs)
        print(user)
        # 签发token，并将user和token存放到序列化对象中
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        self.user = user
        self.token = token
        print(token)
        return attrs

    def _many_method_login(self, **attrs):
        username = attrs.get('username')
        print(username)
        password = attrs.get('password')
        print(password)
        if re.match(r'.*@.*', username):
            print(12)
            user = models.UserInfo.objects.filter(email=username).first()  # type: models.UserInfo

        elif re.match(r'^1[3-9][0-9]{9}$', username):
            user = models.UserInfo.objects.filter(phone=username).first()
        else:
            user = models.UserInfo.objects.filter(username=username).first()

        if not user:
            raise serializers.ValidationError({'username': '账号有误'})

        if not user.check_password(password):
            raise serializers.ValidationError({'password': '密码有误'})

        return user

class LoginMobileSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(write_only=True, min_length=11, max_length=11)
    code = serializers.CharField(write_only=True, min_length=4, max_length=4)
    class Meta:
        model = models.UserInfo
        fields = ('mobile', 'code')

    def validate_mobile(self, value):
        if re.match(r'^1[3-9][0-9]{9}$', value):
            return value
        raise serializers.ValidationError('手机号格式有误')

    def validate_code(self, value):
        try:
            int(value)
            return value
        except:
            raise serializers.ValidationError('验证码格式有误')

    # 校验user，签发token，保存到serializer
    def validate(self, attrs):
        user = self._get_user(**attrs)

        # 签发token，并将user和token存放到序列化对象中
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        self.user = user
        self.token = token

        return attrs

    # 获取用户
    def _get_user(self, **attrs):
        mobile = attrs.get('mobile')
        code = attrs.get('code')
        user = models.UserInfo.objects.filter(mobile=mobile).first()
        if not user:
            raise serializers.ValidationError({'mobile': '该手机号未注册'})

        # 拿到之前缓存的验证码
        old_code = cache.get(settings.SMS_CACHE_KEY % mobile)
        if code != old_code:
            raise serializers.ValidationError({'code': '验证码有误'})
        # 为了保证验证码安全，验证码验证成功后，失效
        # cache.set(settings.SMS_CACHE_KEY % mobile, '0000', 0)
        return user
class RegisterMobileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField()

    code = serializers.CharField(write_only=True, min_length=4, max_length=4)
    class Meta:
        model = models.UserInfo
        fields = ('nickname', 'phone', 'password', 'avatar', 'email','code')
        extra_kwargs = {
            'nickname': {
                'min_length': 1,
                'max_length': 8
            },
            'phone': {
                'min_length': 11,
                'max_length': 11
            },
            'password': {
                'min_length': 6,
                'max_length': 18
            },
        }

    def validate_nickname(self, value):
        # 密码不能包含或必须包含哪些字符
        return value

    def validate_phone(self, value):
        print(78)
        if re.match(r'^1[3-9][0-9]{9}$', value):
            return value
        raise serializers.ValidationError('手机号格式有误')

    def validate_email(self, value):
        print(78)
        if re.match(r'.*@.*', value):
            print(value)
            return value
        raise serializers.ValidationError('邮箱格式有误')

    def validate_code(self, value):
        try:
            int(value)
            return value
        except:
            raise serializers.ValidationError('验证码格式有误')

    def validate_password(self, value):
        # 密码不能包含或必须包含哪些字符
        return value

        # 拿出不入库的数据，塞入额外要入库的数据

    def validate(self, attrs):
        # nickname = attrs.get('nickname')
        phone = attrs.get('phone')
        code = attrs.pop('code')
        old_code = cache.get(settings.SMS_CACHE_KEY % phone)
        if code != old_code:
            raise serializers.ValidationError({'code': '验证码有误'})
        # cache.set(settings.SMS_CACHE_KEY % mobd ile, '0000', 0)  # 清除一次性验证码

        attrs['username'] = phone
        print(attrs)

        return attrs

        # User表必须重写create方法，才能操作密文密码

    def create(self, validated_data):
        print(validated_data)
        return models.UserInfo.objects.create_user(**validated_data)


class RegistersMobileSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True, min_length=4, max_length=4)
    class Meta:
        model = models.UserInfo
        fields = ('nickname', 'phone', 'password', 'email','code')
        extra_kwargs = {
            'nickname': {
                'min_length': 1,
                'max_length': 8
            },
            'phone': {
                'min_length': 11,
                'max_length': 11
            },
            'password': {
                'min_length': 6,
                'max_length': 18
            },
        }

    def validate_nickname(self, value):
        # 密码不能包含或必须包含哪些字符
        return value

    def validate_phone(self, value):
        print(78)
        if re.match(r'^1[3-9][0-9]{9}$', value):
            return value
        raise serializers.ValidationError('手机号格式有误')

    def validate_email(self, value):
        print(78)
        if re.match(r'.*@.*', value):
            return value
        raise serializers.ValidationError('邮箱格式有误')

    def validate_code(self, value):
        try:
            int(value)
            return value
        except:
            raise serializers.ValidationError('验证码格式有误')

    def validate_password(self, value):
        # 密码不能包含或必须包含哪些字符
        return value

        # 拿出不入库的数据，塞入额外要入库的数据

    def validate(self, attrs):
        # nickname = attrs.get('nickname')
        phone = attrs.get('phone')
        code = attrs.pop('code')
        old_code = cache.get(settings.SMS_CACHE_KEY % phone)
        if code != old_code:
            raise serializers.ValidationError({'code': '验证码有误'})
        # cache.set(settings.SMS_CACHE_KEY % mobile, '0000', 0)  # 清除一次性验证码
        blog = models.Blogs.objects.create()
        attrs['username'] = phone
        attrs['blogs'] = blog


        print(attrs)

        return attrs

        # User表必须重写create方法，才能操作密文密码

    def create(self, validated_data):
        print(validated_data)
        return models.UserInfo.objects.create_user(**validated_data)


class AvatarModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)

    class Meta:
        model = models.UserInfo
        fields = ('username',)

    # 校验user，签发token，保存到serializer
    # 那种drf-jwt
    def validate(self, attrs):
        # user = authenticate(**attrs)
        # 账号密码登录 => 多方式登录
        user = self._many_method_login(**attrs)

        # 签发token，并将user和token存放到序列化对象中
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        self.user = user
        self.token = token
        print(token)
        return attrs

    def _many_method_login(self, **attrs):
        username = attrs.get('username')
        print(username)
        user = models.UserInfo.objects.filter(username=username).first()

        return user


class AdvertisingModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)

    class Meta:
        model = models.UserInfo
        fields = ('username',)

    # 校验user，签发token，保存到serializer
    # 那种drf-jwt
    def validate(self, attrs):
        # user = authenticate(**attrs)
        # 账号密码登录 => 多方式登录
        userdetail = self._many_method_login(**attrs)

        # 签发token，并将user和token存放到序列化对象中

        self.userdetail = userdetail

        return attrs

    def _many_method_login(self, **attrs):
        username = attrs.get('username')
        try:
            user = models.UserInfo.objects.filter(username=username).first()
            print(12)
            userdetail = user.userdetails
            return userdetail
        except:
            raise serializers.ValidationError({'username': '您未完善'})


class InterMobileSerializer(serializers.ModelSerializer):
    details = serializers.CharField()
    introduce = serializers.CharField()
    advertising = serializers.ImageField()

    class Meta:
        model = models.UserDetails
        fields = ('details', 'introduce','advertising')
        extra_kwargs = {
            'details': {
                'min_length': 0,
                'max_length': 30
            },
            'introduce': {
                'min_length': 0,
                'max_length': 200
            },
        }

    def validate_details(self, value):
        print(value)
        return value

    def validate_introduce(self, value):
        print(2223, value)
        return value

    def validate(self, attrs):
        print(885, attrs)
        return attrs

class InterMobilessSerializer(serializers.ModelSerializer):
    details = serializers.CharField()
    introduce = serializers.CharField()


    class Meta:
        model = models.UserDetails
        fields = ('details', 'introduce')
        extra_kwargs = {
            'details': {
                'min_length': 0,
                'max_length': 30
            },
            'introduce': {
                'min_length': 0,
                'max_length': 200
            },
        }

    def validate_details(self, value):
        print(value)
        return value

    def validate_introduce(self, value):
        print(2223, value)
        return value

    def validate(self, attrs):
        print(885, attrs)
        return attrs


class ChangeinformationsMobileSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField()
    password = serializers.CharField()
    avatar = serializers.ImageField()

    class Meta:
        model = models.UserDetails
        fields = ('nickname', 'password', 'avatar')
        extra_kwargs = {
            'nickname': {
                'min_length': 1,
                'max_length': 8
            },
            'password': {
                'min_length': 6,
                'max_length': 18
            },
        }

    def validate_details(self, value):
        print(value)
        return value

    def validate_introduce(self, value):
        print(2223, value)
        return value

    def validate(self, attrs):
        print(885, attrs)
        return attrs

    def create(self, validated_data):
        print(validated_data)

        user = models.UserInfo.objects.create_user(**validated_data)

        return user


class ChangeinformationMobileSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = models.UserDetails
        fields = ('nickname', 'password',)
        extra_kwargs = {
            'nickname': {
                'min_length': 1,
                'max_length': 8
            },
            'password': {
                'min_length': 6,
                'max_length': 18
            },
        }

    def validate_details(self, value):
        print(value)
        return value

    def validate_introduce(self, value):
        print(2223, value)
        return value

    def validate(self, attrs):
        print(885, attrs)
        return attrs

    def create(self, validated_data):
        print(validated_data)
        return models.UserInfo.objects.create_user(**validated_data)


class ArticleModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)

    # class Meta:
    #     model = models.Article
    #     fields = ('title','intro','content','picture','create_time')
    class Meta:
        model = models.UserInfo
        fields = ('username',)

    def validate(self, attrs):
        # user = authenticate(**attrs)
        # 账号密码登录 => 多方式登录
        return attrs


class ArticleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Article
        fields = '__all__'


class ArticlesModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Article
        fields = '__all__'
class CommentModelSerializer(serializers.ModelSerializer):
    # user = serializers.CharField()
    # article = serializers.CharField()
    content = serializers.CharField()
    # parent = serializers.CharField()

    class Meta:
        model = models.Comment
        fields = ('content',)

    def validate(self, attrs):
        print(633, attrs)
        return attrs
class Comment_listModelSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField()
    user_id = serializers.CharField()
    avatar = serializers.ImageField()
    class Meta:
        model = models.Comment
        fields = ('id','is_delete','is_show','created_time','content','create_time','updated_time','article','parent','user','nickname','user_id','avatar')
    def validate(self, attrs):
        print(123)
        # nickname = attrs.get('nickname')
        user = attrs.get('nickname')
        user_id = attrs.get('user_id')
        avatar = attrs.get('avatar')
        attrs['nickname'] = user
        attrs['user_id'] = user_id
        attrs['avatar'] = avatar

        print(attrs)

        return attrs
class Comment_listsModelSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField()
    user_id = serializers.CharField()
    avatar = serializers.ImageField()
    parent_name = serializers.CharField()
    class Meta:
        model = models.Comment
        fields = ('id','is_delete','is_show','created_time','content','create_time','updated_time','article','parent','user','nickname','user_id','avatar','parent_name')
    def validate(self, attrs):
        print(123)
        # nickname = attrs.get('nickname')
        user = attrs.get('nickname')
        user_id = attrs.get('user_id')
        avatar = attrs.get('avatar')
        parent_name = attrs.get('parent_name')
        attrs['nickname'] = user
        attrs['user_id'] = user_id
        attrs['avatar'] = avatar
        attrs['parent_name'] = parent_name

        print(attrs)

        return attrs

# class UserModelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.UserInfo
#         fields = '__all__'
class ArticleslistModelSerializer(serializers.ModelSerializer):
    # user = UserModelSerializer()
    nickname = serializers.CharField()
    user_id = serializers.CharField()
    class Meta:
        model = models.Article
        fields = ('id','is_delete','is_show','created_time','updated_time','title','intro','content','comment_num','up_num','down_num','picture','create_time','blogs','category','tags','nickname','user_id')
        # fields = '__all__'
    def validate(self, attrs):
        print(123)
        # nickname = attrs.get('nickname')
        user = attrs.get('nickname')
        user_id = attrs.get('user_id')
        print(user)
        # code = attrs.pop('code')
        # old_code = cache.get(settings.SMS_CACHE_KEY % phone)
        # if code != old_code:
        #     raise serializers.ValidationError({'code': '验证码有误'})
        # # cache.set(settings.SMS_CACHE_KEY % mobile, '0000', 0)  # 清除一次性验证码
        # user=models.UserInfo.objects.filter(id=user).first()
        print(user)
        attrs['nickname'] = user
        attrs['user_id'] = user_id

        print(attrs)

        return attrs


class CategorysModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'

class TagModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = '__all__'


class CategoryMobileSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = models.Category
        fields = ('name',)
        extra_kwargs = {
            'name': {
                'min_length': 0,
                'max_length': 30
            },

        }

    def validate_name(self, value):
        print(value)
        return value

    def validate(self, attrs):
        print(633, attrs)
        return attrs


class TagMobileSerializer(serializers.ModelSerializer):


    class Meta:
        model = models.Tag
        fields ='__all__'


class BackgroundMobileSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    intro = serializers.CharField()
    content = serializers.CharField()
    picture = serializers.ImageField()

    class Meta:
        model = models.Article
        fields = ('title', 'intro', 'content', 'picture')

    def validate_name(self, value):
        print(value)
        return value

    def validate(self, attrs):
        print(633, attrs)
        return attrs


class BackgroundsMobileSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    intro = serializers.CharField()
    content = serializers.CharField()

    class Meta:
        model = models.Article
        fields = ('title', 'intro', 'content')

    def validate_name(self, value):
        print(value)
        return value

    def validate(self, attrs):
        print(633, attrs)
        return attrs

class PictureMobileSerializer(serializers.ModelSerializer):
    picture = serializers.ImageField()

    class Meta:
        model = models.Pictures
        fields = ('picture', )



    def validate(self, attrs):
        print(885, attrs)
        return attrs