from django.views import View

from App.models import App, Scope, UserApp
from Base.policy import get_logo_policy
from Base.qn import QN_RES_MANAGER
from Base.valid_param import ValidParam
from Base.validator import require_get, require_login, require_post, require_put, require_delete, \
    require_json, require_scope, maybe_login
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
    @require_get([
        ValidParam('relation').df(App.R_USER).p(relation_process),
        ValidParam('frequent').df(),
        ValidParam('count').df(3).p(int),
    ])
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
            app_list = [o_app.to_dict(base=True) for o_app in o_apps]
        else:
            frequent = request.d.frequent
            count = request.d.count
            user_app_list = UserApp.get_user_app_list_by_o_user(o_user, frequent, count)
            app_list = [o_user_app.app.to_dict(base=True) for o_user_app in user_app_list]
        return response(body=app_list)

    @staticmethod
    @require_json
    @require_post([
        'name',
        'info',
        'description',
        'redirect_uri',
        ValidParam('scopes').p(Scope.list_to_scope_list),
    ])
    @require_login
    @require_scope(deny_all_auth_token=True)
    def post(request):
        """POST /api/app/

        创建我的app
        """
        o_user = request.user
        name = request.d.name
        info = request.d.info
        description = request.d.description
        redirect_uri = request.d.redirect_uri
        scopes = request.d.scopes

        ret = App.create(name, description, redirect_uri, scopes, o_user, info)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_app = ret.body
        return response(body=o_app.to_dict())


class AppIDSecretView(View):
    @staticmethod
    @require_get()
    @require_login
    @require_scope(deny_all_auth_token=True)
    def get(request, app_id):
        """GET /api/app/:app_id/secret"""
        o_user = request.user

        ret = App.get_app_by_id(app_id)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_app = ret.body
        if not isinstance(o_app, App):
            return error_response(Error.STRANGE)

        if not o_app.belong(o_user):
            return error_response(Error.APP_NOT_BELONG)

        return response(body=o_app.secret)


class AppIDView(View):
    @staticmethod
    @require_get()
    @maybe_login
    @require_scope(deny_all_auth_token=True, allow_no_login=True)
    def get(request, app_id):
        """GET /api/app/:app_id

        获取应用信息以及用户与应用的关系（属于、绑定、打分，仅限用户登录时）
        """
        o_user = request.user

        ret = App.get_app_by_id(app_id)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_app = ret.body
        if not isinstance(o_app, App):
            return error_response(Error.STRANGE)

        dict_ = o_app.to_dict()

        ret = UserApp.get_user_app_by_o_user_o_app(o_user, o_app)
        if ret.error is not Error.OK:
            relation = dict(bind=False, rebind=False, mark=0, belong=False)
        else:
            o_user_app = ret.body
            if not isinstance(o_user_app, UserApp):
                return error_response(Error.STRANGE)
            relation = o_user_app.to_dict()

        relation['belong'] = o_app.belong(o_user)
        dict_['relation'] = relation

        dict_['belong'] = relation['belong']  # 老版本兼容

        return response(body=dict_)

    @staticmethod
    @require_json
    @require_put([
        'name',
        'description',
        'redirect_uri',
        ValidParam('scopes').p(Scope.list_to_scope_list),
    ])
    @require_login
    @require_scope(deny_all_auth_token=True)
    def put(request, app_id):
        o_user = request.user
        name = request.d.name
        desc = request.d.description
        redirect_uri = request.d.redirect_uri
        scopes = request.d.scopes

        ret = App.get_app_by_id(app_id)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_app = ret.body
        if not isinstance(o_app, App):
            return error_response(Error.STRANGE)

        if not o_app.belong(o_user):
            return error_response(Error.APP_NOT_BELONG)

        ret = o_app.modify(name, desc, redirect_uri, scopes)
        if ret.error is not Error.OK:
            return error_response(ret)
        return response(body=o_app.to_dict())

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
        if not o_app.belong(o_user):
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
        qn_token, key = QN_RES_MANAGER.get_upload_token(key, get_logo_policy(app_id))
        return response(body=dict(upload_token=qn_token, key=key))

    @staticmethod
    @require_json
    @require_post(['key', 'app_id'])
    def post(request):
        """ POST /api/app/logo

        七牛上传应用logo回调函数
        """
        ret = QN_RES_MANAGER.qiniu_auth_callback(request)
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


class UserAppIdView(View):
    @staticmethod
    @require_json
    @require_post(['app_secret'])
    def post(request, user_app_id):
        """ POST /api/app/user/:user_app_id

        通过app获取user信息
        """

        app_secret = request.d.app_secret

        ret = UserApp.get_user_app_by_user_app_id(user_app_id)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_user_app = ret.body
        if not isinstance(o_user_app, UserApp):
            return error_response(Error.STRANGE)

        if not o_user_app.app.authentication(app_secret):
            return error_response(Error.ERROR_APP_SECRET)

        return response(body=o_user_app.user.to_dict())


@require_get()
def refresh_frequent_score(request):
    ret = UserApp.refresh_frequent_score()
    return error_response(ret)
