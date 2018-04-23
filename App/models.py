import datetime

from django.db import models
from django.utils.crypto import get_random_string

from Base.common import deprint
from Base.validator import field_validator
from Base.error import Error
from Base.jtoken import jwt_e, JWType
from Base.response import Ret


class Scope(models.Model):
    """权限类"""
    L = {
        'name': 10,
        'desc': 20,
    }
    name = models.CharField(
        verbose_name='权限英文简短名称',
        max_length=L['name'],
        unique=True,
    )
    desc = models.CharField(
        verbose_name='权限介绍',
        max_length=L['desc'],
    )
    always = models.NullBooleanField(
        verbose_name="Null 可有可无 True 一直可选 False 一直不可选",
        default=None,
    )
    FIELD_LIST = ['name', 'desc']

    class __ScopeNone:
        pass

    @classmethod
    def _validate(cls, d):
        return field_validator(d, cls)

    @classmethod
    def get_scope_by_id(cls, sid):
        try:
            o_scope = cls.objects.get(pk=sid)
        except cls.DoesNotExist as err:
            deprint('Scope-get_scope_by_id', str(err))
            return Ret(Error.NOT_FOUND_SCOPE)
        return Ret(o_scope)

    @classmethod
    def get_scope_by_name(cls, name, default=__ScopeNone()):
        try:
            o_scope = cls.objects.get(name=name)
        except Exception as err:
            deprint(str(err))
            if isinstance(default, cls.__ScopeNone):
                return Ret(Error.NOT_FOUND_SCOPE)
            else:
                return Ret(default)
        return Ret(o_scope)

    @classmethod
    def create(cls, name, desc):
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret

        try:
            o_scope = cls(
                name=name,
                desc=desc,
            )
            o_scope.save()
        except Exception as err:
            deprint('create-scope', str(err))
            return Ret(Error.ERROR_CREATE_SCOPE)
        return Ret(o_scope)

    def to_dict(self):
        return dict(
            sid=self.pk,
            name=self.name,
            desc=self.desc,
            always=self.always,
        )

    @classmethod
    def list_to_scope_list(cls, scopes):
        scope_list = []
        if not isinstance(scopes, list):
            return []
        for sid in scopes:
            ret = cls.get_scope_by_id(sid)
            if ret.error is Error.OK:
                scope_list.append(ret.body)
        return scope_list

    @classmethod
    def get_scope_list(cls):
        scopes = cls.objects.all()
        return [o_scope.to_dict() for o_scope in scopes];


class App(models.Model):
    L = {
        'name': 32,
        'id': 32,
        'secret': 32,
        'redirect_uri': 512,
        'desc': 32,
        'logo': 1024,
    }
    MIN_L = {
        'name': 2,
    }

    R_USER = 'user'
    R_OWNER = 'owner'
    R_LIST = [R_USER, R_OWNER]

    name = models.CharField(
        verbose_name='应用名称',
        max_length=L['name'],
        unique=True,
    )
    id = models.CharField(
        verbose_name='应用唯一ID',
        max_length=L['id'],
        primary_key=True,
    )
    secret = models.CharField(
        verbose_name='应用密钥',
        max_length=L['secret'],
    )
    redirect_uri = models.URLField(
        verbose_name='应用跳转URI',
        max_length=L['redirect_uri'],
    )
    scopes = models.ManyToManyField(
        'Scope',
        default=None,
    )
    owner = models.ForeignKey(
        'User.User',
        on_delete=models.CASCADE,
        db_index=True,
    )
    field_change_time = models.FloatField(
        null=True,
        blank=True,
        default=0,
    )
    desc = models.CharField(
        max_length=L['desc'],
        default=None,
    )
    logo = models.CharField(
        default=None,
        null=True,
        blank=True,
        max_length=L['logo'],
    )

    FIELD_LIST = ['name', 'id', 'secret', 'redirect_uri', 'scope', 'desc', 'logo']

    @classmethod
    def _validate(cls, d, allow_none=False):
        return field_validator(d, cls, allow_none=allow_none)

    @classmethod
    def get_app_by_name(cls, name):
        try:
            o_app = cls.objects.get(name=name)
        except cls.DoesNotExist as err:
            deprint('App-get_app_by_name', str(err))
            return Ret(Error.NOT_FOUND_APP)
        return Ret(o_app)

    @classmethod
    def get_app_by_id(cls, app_id):
        try:
            o_app = cls.objects.get(pk=app_id)
        except cls.DoesNotExist as err:
            deprint('App-get_app_by_id', str(err))
            return Ret(Error.NOT_FOUND_APP)
        return Ret(o_app)

    @classmethod
    def get_unique_app_id(cls):
        while True:
            app_id = get_random_string(length=cls.L['id'])
            ret = cls.get_app_by_id(app_id)
            if ret.error == Error.NOT_FOUND_APP:
                return app_id
            deprint('generate app_id: %s, conflict.' % app_id)

    @classmethod
    def get_apps_by_owner(cls, owner):
        return cls.objects.filter(owner=owner)

    @classmethod
    def create(cls, name, desc, redirect_uri, scopes, owner):
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret

        ret = cls.get_app_by_name(name)
        if ret.error is Error.OK:
            return Ret(Error.EXIST_APP_NAME)

        try:
            o_app = cls(
                name=name,
                desc=desc,
                id=cls.get_unique_app_id(),
                secret=get_random_string(length=cls.L['secret']),
                redirect_uri=redirect_uri,
                owner=owner,
                field_change_time=datetime.datetime.now().timestamp(),
            )
            o_app.save()
            o_app.scopes.add(*scopes)
            o_app.save()
        except Exception as err:
            deprint('App-create', str(err))
            return Ret(Error.ERROR_CREATE_APP, append_msg=str(err))
        return Ret(o_app)

    def modify(self, name, desc, redirect_uri, scopes):
        """修改应用信息"""
        ret = self._validate(locals())
        if ret.error is not Error.OK:
            return ret
        self.name = name
        self.desc = desc
        self.redirect_uri = redirect_uri
        self.scopes.remove()
        self.scopes.add(*scopes)
        self.field_change_time = datetime.datetime.now().timestamp()
        try:
            self.save()
        except Exception as err:
            deprint(str(err))
            return Ret(Error.ERROR_MODIFY_APP, append_msg=str(err))
        return Ret()

    def to_dict(self, relation=R_USER):
        scopes = self.scopes.all()
        scope_list = [o_scope.to_dict() for o_scope in scopes]

        dict_ = dict(
            app_name=self.name,
            app_id=self.id,
            scopes=scope_list,
            redirect_uri=self.redirect_uri,
            logo=self.get_logo_url(),
            app_desc=self.desc,
            owner=self.owner.to_dict(),
        )
        if relation == App.R_OWNER:
            dict_['app_secret'] = self.secret
        return dict_

    def get_logo_url(self, small=True):
        """获取应用logo地址"""
        if self.logo is None:
            return None
        from Base.qn import QN_RES_MANAGER
        key = "%s-small" % self.logo if small else self.logo
        return QN_RES_MANAGER.get_resource_url(key)

    def modify_logo(self, logo):
        """修改应用logo"""
        ret = self._validate(locals())
        if ret.error is not Error.OK:
            return ret
        from Base.qn import QN_RES_MANAGER
        if self.logo:
            ret = QN_RES_MANAGER.delete_res(self.logo)
            if ret.error is not Error.OK:
                return ret
        self.logo = logo
        self.save()
        return Ret()

    def belong(self, o_user):
        return self.owner == o_user

    def authentication(self, app_secret):
        return self.secret == app_secret


class UserApp(models.Model):
    """用户应用类"""
    L = {
        'user_app_id': 16,
        'auth_code': 32,
    }

    user = models.ForeignKey(
        'User.User',
        on_delete=models.CASCADE,
    )
    app = models.ForeignKey(
        'App.App',
        on_delete=models.CASCADE,
    )
    user_app_id = models.CharField(
        max_length=L['user_app_id'],
        verbose_name='用户在这个app下的唯一ID',
        unique=True,
    )
    bind = models.BooleanField(
        default=False,
        verbose_name='用户是否绑定应用',
    )
    last_auth_code_time = models.DecimalField(
        default=0,
        max_digits=16,
        decimal_places=6,
        verbose_name='上一次申请auth_code的时间，防止被多次使用',
    )

    def to_dict(self):
        return dict(
            user=self.user.to_dict(),
            app=self.app.to_dict(relation=App.R_USER),
            user_app_id=self.user_app_id,
            bind=self.bind,
        )

    @classmethod
    def get_user_app_list_by_o_user(cls, o_user):
        return cls.objects.filter(user=o_user, bind=True)

    @classmethod
    def get_user_app_by_o_user_o_app(cls, o_user, o_app):
        try:
            o_user_app = cls.objects.get(user=o_user, app=o_app)
        except cls.DoesNotExist as err:
            deprint('UserApp-get_user_app_by_o_user_o_app', str(err))
            return Ret(Error.NOT_FOUND_USER_APP)
        return Ret(o_user_app)

    @classmethod
    def get_user_app_by_user_app_id(cls, user_app_id, check_bind=False):
        try:
            o_user_app = cls.objects.get(user_app_id=user_app_id)
        except cls.DoesNotExist as err:
            deprint('UserApp-get_user_app_by_user_app_id')
            return Ret(Error.NOT_FOUND_USER_APP)
        if check_bind and not o_user_app.bind:
            return Ret(Error.APP_UNBINDED)
        return Ret(o_user_app)

    @classmethod
    def get_unique_user_app_id(cls):
        while True:
            user_app_id = get_random_string(length=cls.L['user_app_id'])
            ret = cls.get_user_app_by_user_app_id(user_app_id)
            if ret.error == Error.NOT_FOUND_USER_APP:
                return user_app_id
            deprint('generate user_app_id: %s, conflict.' % user_app_id)

    @classmethod
    def do_bind(cls, o_user, o_app):
        crt_timestamp = datetime.datetime.now().timestamp()

        ret = cls.get_user_app_by_o_user_o_app(o_user, o_app)
        if ret.error is Error.OK:
            o_user_app = ret.body
            if not isinstance(o_user_app, cls):
                return Ret(Error.STRANGE)
            o_user_app.bind = True
            o_user_app.last_auth_code_time = crt_timestamp
            o_user_app.save()
        else:
            try:
                o_user_app = cls(
                    user=o_user,
                    app=o_app,
                    user_app_id=cls.get_unique_user_app_id(),
                    bind=True,
                    last_auth_code_time=crt_timestamp
                )
                o_user_app.save()
            except Exception as err:
                deprint(str(err))
                return Ret(Error.ERROR_BIND_USER_APP)
        return jwt_e(dict(
            user_app_id=o_user_app.user_app_id,
            type=JWType.AUTH_CODE,
            ctime=crt_timestamp
        ), replace=False, expire_second=5 * 60)

    @classmethod
    def check_bind(cls, o_user, o_app):
        ret = cls.get_user_app_by_o_user_o_app(o_user, o_app)
        if ret.error is not Error.OK:
            return False
        o_user_app = ret.body
        if not isinstance(o_user_app, UserApp):
            deprint('UserApp-check_bind_strange')
            return False
        return o_user_app.bind
