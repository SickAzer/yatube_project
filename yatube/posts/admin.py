from django.contrib import admin

from .models import Post, Group, Comment, Follow, Like


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'title',
                    'text',
                    'created',
                    'author',
                    'group',
                    'image',
                    'like_count'
                    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'title',
                    'slug',
                    'description',
                    'creator'
                    )
    search_fields = ('title',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'text',
                    'post',
                    'author',
                    )
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'author',
                    )
    empty_value_display = '-пусто-'
    
admin.site.register(Like)