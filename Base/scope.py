from App.models import Scope


class ScopeInstance:
    read_base_info = Scope.get_by_name('readBaseInfo')
    write_base_info = Scope.get_by_name('writeBaseInfo')
    send_email = Scope.get_by_name('sendEmail')
    send_mobile = Scope.get_by_name('sendMobile')
    read_app_list = Scope.get_by_name('readMyAppList')
    assert read_base_info
    assert write_base_info
    assert send_email
    assert send_mobile
    assert read_app_list


SI = ScopeInstance
