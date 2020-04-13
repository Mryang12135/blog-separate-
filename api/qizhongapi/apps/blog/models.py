from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.model import BaseModel


class UserInfo(AbstractUser):
    phone = models.CharField(max_length=11, unique=True)
    avatar = models.FileField(upload_to='avatar', default='avatar/default.png')
    nickname = models.CharField(max_length=255, default='Tim')
    create_time = models.DateField(auto_now_add=True)
    is_vip = models.BigIntegerField(default=0)
    blogs = models.OneToOneField('Blogs', to_field='id', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '用户'

    def __str__(self):
        return self.nickname
    # @property
    # def blog(self):
    #     self.Article.title
    # pass


class UserDetails(BaseModel):
    advertising = models.FileField(upload_to='advertising', default='advertising/ad-placeholder.jpg')
    details = models.CharField(max_length=255, null=True)
    introduce = models.TextField(null=True)
    user = models.OneToOneField('UserInfo', to_field='id', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '用户详情'


class Advertising(BaseModel):
    name = models.CharField(max_length=255, null=True)
    advertising = models.FileField(upload_to='advertising', default='advertising/ad-placeholder.jpg')
    user = models.ForeignKey(to='UserInfo', to_field='id', null=True, on_delete=models.DO_NOTHING)


class Blogs(BaseModel):
    site_name = models.CharField(max_length=32,null=True)
    site_title = models.CharField(max_length=64,null=True)

    class Meta:
        verbose_name_plural = '站点'


class Tag(BaseModel):
    name = models.CharField(max_length=32)
    blog = models.ForeignKey(to='Blogs', to_field='id', null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class Category(BaseModel):
    name = models.CharField(max_length=64, null=True)
    blog = models.ForeignKey(to='Blogs', to_field='id', null=True, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name_plural = '文章分类'

    def __str__(self):
        return self.name


class File(BaseModel):
    file = models.FileField(upload_to='file', verbose_name='文件链接')
    level = models.CharField(max_length=64,null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    blogs = models.ForeignKey(to='Blogs', to_field='id', null=True, on_delete=models.DO_NOTHING)
    tags = models.ManyToManyField(to='Tag', through='File2Tag', through_fields=('file', 'tag'))


class File2Tag(BaseModel):
    file = models.ForeignKey(to='File', to_field='id', null=True, on_delete=models.DO_NOTHING)
    tag = models.ForeignKey(to='Tag', to_field='id', null=True, on_delete=models.DO_NOTHING)


class Article(BaseModel):
    title = models.CharField(max_length=64)
    intro = models.CharField(max_length=255)
    content = models.TextField()
    comment_num = models.BigIntegerField(default=0)
    up_num = models.BigIntegerField(default=0)
    down_num = models.BigIntegerField(default=0)
    picture = models.FileField(upload_to='picture', verbose_name='图片链接',default='picture/aa.jpg')
    create_time = models.DateField(auto_now_add=True)
    blogs = models.ForeignKey(to='Blogs', to_field='id', null=True, on_delete=models.DO_NOTHING)
    category = models.ForeignKey(to='Category', to_field='id', null=True, on_delete=models.DO_NOTHING)
    tags = models.ManyToManyField(to='Tag', through='Article2Tag', through_fields=('article', 'tag'))

    class Meta:
        verbose_name_plural = '文章'

    def __str__(self):
        return self.title
      

class Pictures(BaseModel):
    picture = models.FileField(upload_to='picture', verbose_name='图片链接')
    article = models.ForeignKey(to='Article', to_field='id', null=True, on_delete=models.DO_NOTHING)


class Article2Tag(BaseModel):
    article = models.ForeignKey(to='Article', to_field='id', null=True, on_delete=models.DO_NOTHING)
    tag = models.ForeignKey(to='Tag', to_field='id', null=True, on_delete=models.DO_NOTHING)


class UpAndDown(BaseModel):
    user = models.ForeignKey(to='UserInfo', to_field='id', null=True, on_delete=models.DO_NOTHING)
    article = models.ForeignKey(to='Article', to_field='id', null=True, on_delete=models.DO_NOTHING)
    is_up = models.BooleanField()  # 传True/False   存1/0


class Comment(BaseModel):
    user = models.ForeignKey(to='UserInfo', to_field='id', null=True, on_delete=models.DO_NOTHING)
    article = models.ForeignKey(to='Article', to_field='id', null=True, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=255)
    create_time = models.DateField(auto_now_add=True)
    parent = models.ForeignKey(to='self', to_field='id', null=True, on_delete=models.DO_NOTHING)
