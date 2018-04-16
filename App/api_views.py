from django.views import View

from App.models import App, Scope, UserApp
from Base.policy import get_avatar_policy, get_logo_policy
from Base.qn import get_upload_token, qiniu_auth_callback
from Base.validator import require_get, require_login, require_post, require_put, require_delete, \
    require_json, require_scope
from Base.error import Error
from Base.response import error_response, response
from User.models import User


class AppView(View):
    @staticmethod
    def relation_process(relation):
        if relation not in App.R_LIST:
            relation = App.R_USER
        return relation

    @staticmethod
    @require_get([{
        "value": 'relation',
        "default": True,
        "default_value": App.R_USER,
        "process": relation_process,
    }])
    @require_login
    @require_scope(deny_all_auth_token=True)
    def get(request):
        """GET /api/app/

        获取与我相关的app列表
        """
        o_user = request.user
        relation = request.d.relation

        if relation == App.R_OWNER:
            o_apps = App.get_apps_by_owner(o_user)
            app_list = [o_app.to_dict(relation=relation) for o_app in o_apps]
        else:
            user_app_list = UserApp.get_user_app_list_by_o_user(o_user)
            app_list = [o_user_app.app.to_dict(relation=relation) for o_user_app in user_app_list]
        return response(body=app_list)

    @staticmethod
    @require_json
    @require_post([
        'name',
        'description',
        'redirect_uri',
        {
            "value": 'scopes',
            "process": Scope.list_to_scope_list,
        }
    ])
    @require_login
    @require_scope(deny_all_auth_token=True)
    def post(request):
        """POST /api/app/

        创建我的app
        """
        o_user = request.user
        name = request.d.name
        description = request.d.description
        redirect_uri = request.d.redirect_uri
        scopes = request.d.scopes

        ret = App.create(name, description, redirect_uri, scopes, o_user)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_app = ret.body
        return response(body=o_app.to_dict(relation=App.R_OWNER))


class AppIDView(View):
    @staticmethod
    @require_get()
    def get(request, app_id):
        """GET /api/app/:app_id"""
        ret = App.get_app_by_id(app_id)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_app = ret.body
        if not isinstance(o_app, App):
            return error_response(Error.STRANGE)

        return response(body=o_app.to_dict(relation=App.R_USER))

    @staticmethod
    @require_json
    @require_put([('name', None, None), ('redirect_uri', None, None)])
    @require_login
    @require_scope(deny_all_auth_token=True)
    def put(request, app_id):
        o_user = request.user
        name = request.d.name
        redirect_uri = request.d.redirect_uri

        ret = App.get_app_by_id(app_id)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_app = ret.body
        if o_app.owner is not o_user:
            return error_response(Error.APP_NOT_BELONG)

        ret = o_app.modify(name, redirect_uri)
        if ret.error is not Error.OK:
            return error_response(ret)
        return response(body=o_app.to_dict(relation=App.R_OWNER))

    @staticmethod
    @require_delete()
    @require_login
    @require_scope(deny_all_auth_token=True)
    def delete(request, app_id):
        o_user = request.user

        ret = App.get_app_by_id(app_id)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_app = ret.body
        if o_app.owner is not o_user:
            return error_response(Error.APP_NOT_BELONG)

        o_app.delete()
        return response()


class ScopeView(View):
    @staticmethod
    @require_get()
    def get(request):
        return response(body=Scope.get_scope_list())


class AppLogoView(View):
    @staticmethod
    @require_get(['filename', 'app_id'])
    @require_login
    @require_scope(deny_all_auth_token=True)
    def get(request):
        """ GET /api/app/logo

        获取七牛上传token
        """
        o_user = request.user
        if not isinstance(o_user, User):
            return error_response(Error.STRANGE)

        filename = request.d.filename
        app_id = request.d.app_id

        ret = App.get_app_by_id(app_id)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_app = ret.body
        if not isinstance(o_app, App):
            return error_response(Error.STRANGE)

        if o_app.owner != o_user:
            return error_response(Error.APP_NOT_BELONG)

        import datetime
        crt_time = datetime.datetime.now().timestamp()
        key = 'app/%s/logo/%s/%s' % (app_id, crt_time, filename)
        qn_token, key = get_upload_token(key, get_logo_policy(app_id))
        return response(body=dict(upload_token=qn_token, key=key))

    @staticmethod
    @require_json
    @require_post(['key', 'app_id'])
    def post(request):
        """ POST /api/app/logo

        七牛上传用户头像回调函数
        """
        ret = qiniu_auth_callback(request)
        if ret.error is not Error.OK:
            return error_response(ret)

        key = request.d.key
        app_id = request.d.app_id
        ret = App.get_app_by_id(app_id)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_app = ret.body
        if not isinstance(o_app, App):
            return error_response(Error.STRANGE)
        o_app.modify_logo(key)
        return response(body=o_app.to_dict())
