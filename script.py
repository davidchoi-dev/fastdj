import os, sys, platform
try:
    setup_file = __import__(sys.argv[1])
except:
    print("Try with an argument")
    exit()


class ProjectCommand:  # class about project initializing, like commands
    def __init__(self, prj_name):
        self.prj_name = prj_name

    def setup_venv(self):
        command = ""
        if platform.system() == 'Windows':
            command = "python "
        else:
            command = "python3 "
        command += "-m venv myvenv"
        os.system(command)

    def install_requirements(
            self
    ):  # pip install django djangorestframework django-cors-headers
        os.system("pip install --upgrade pip")
        os.system("pip install django djangorestframework django-cors-headers")

    def start_project(self):
        os.system("django-admin startproject " + str(self.prj_name))

    def create_app(self, app_name):
        origin_directory = os.getcwd()
        os.chdir(f"{os.getcwd()}/{self.prj_name}/")
        os.system(f"python manage.py startapp {app_name}")
        open(f"{os.getcwd()}/{app_name}/urls.py", 'w').close()
        os.chdir(origin_directory)


class ProjectConfigurations:
    def __init__(self, project_name):
        self.settings_file_path = f"{os.getcwd()}/{project_name}/{project_name}/settings.py"
        self.urls_file_path = f"{os.getcwd()}/{project_name}/{project_name}/urls.py"

    def load_settings(self):
        settings_file = open(self.settings_file_path, 'r')
        self.settings = settings_file.read()
        settings_file.close()

    def set_language_code(self, language):
        self.settings = self.settings.replace("LANGUAGE_CODE = en-us",
                                              f"LANGUAGE_CODE = '{language}'")

    def set_timezone(self, timezone):
        self.settings = self.settings.replace("TIME_ZONE = 'UTC'",
                                              f"TIMEZONE = '{timezone}'")

    def load_urls(self):
        urls_file = open(self.urls_file_path, 'r')
        self.urls = urls_file.read()
        urls_file.close()

    def add_module(self, module_name):
        installed_apps_index = self.settings.find("INSTALLED_APPS")
        last_module_index = self.settings.find(
            "]", installed_apps_index) - 1  # except itself and the '\n
        self.settings = self.settings[:
                                      last_module_index] + "\n\t# added by fastdj\n\t'" + module_name + "'," + self.settings[
                                          last_module_index:]

    def add_installed_modules(self):  # djangorestframework django-cors-headers
        modules = ['rest_framework', 'corsheaders']
        for module in modules:
            self.add_module(module)

    def add_token_login_model(self):  # token login model
        self.settings += "\n# added by fastdj\nREST_FRAMEWORK = {\n\t'DEFAULT_AUTHENTICATION_CLASSES': (\n\t\t'rest_framework.authentication.BasicAuthentication',\n\t\t'rest_framework.authentication.TokenAuthentication',\n\t),\n}\n"
        self.add_module('rest_framework.authtoken')

    def set_cross_origin_all(self):  # cors origin allow all
        self.settings += "\n# added by fastdj\nCORS_ORIGIN_ALLOW_ALL = True\nCORS_ALLOW_CREDENTIALS = True\n"

    def set_allowed_hosts_all(self):  # set allowed hosts to all
        self.settings = self.settings.replace("ALLOWED_HOSTS = []",
                                              "ALLOWED_HOSTS = ['*']")

    def add_url_path(self, app_name):
        urlpatterns_index = self.urls.find("urlpatterns")
        last_path_index = self.urls.find(
            "]", urlpatterns_index) - 1  # except itself and the '\n
        self.urls = f"{self.urls[:last_path_index]}\n\t# added by fastdj\n\tpath('{app_name}/', include('{app_name}.urls', name='{app_name}')){self.urls[last_path_index:]}\n"

    def save_settings(self):
        file = open(self.settings_file_path, 'w')
        file.write(self.settings)
        file.close()

    def save_urls(self):
        file = open(self.urls_file_path, 'w')
        file.write(self.urls)
        file.close()


class Field:
    def __init__(self,
                 name,
                 template=None,
                 field=None,
                 options=list(),
                 serializers={}):
        self.name = name
        self.field = field
        self.serializers = serializers
        self.options = options
        if template == "model_owner":
            self.field = "ForeignKey"
            self.options = [
                "'auth.user'", "related_name='article_writer'",
                "on_delete=models.CASCADE", "null=False"
            ]
            self.serializers = {
                "field": "ReadOnlyField",
                "options": ["source='writer.username'"]
            }

    def get_code(self):
        options_str = ""
        for option in self.options:
            options_str += option + ", "
        options_str = options_str[:-2]  # to remove last ", "
        return f"\t{self.name} = models.{self.field}({options_str})\n"


class Model:
    def __init__(self, name):
        self.name = name
        self.fields = list()

    def add_field(self, field):
        self.fields.append(field)

    def get_code(self):
        code = f"class {self.name}(models.Model):\n"
        for field in self.fields:
            code += field.get_code()
        return code


class View:
    def __init__(self,
                 name,
                 template=None,
                 options=None,
                 permissions=None,
                 url_getters=None):
        self.name = name
        self.template = template
        self.options = options
        self.permissions = permissions
        self.url_getters = url_getters


class App:
    def __init__(self, name):
        self.name = name
        self.models = list()
        self.views = list()
        self.models_code = ""
        self.views_code = ""

    def add_model(self, model):
        self.models.append(model)

    def add_view(self, view):
        self.views.append(views)

    def save_models(self, project_name):
        file = open(f"{os.getcwd()}/{project_name}/{self.name}/models.py", 'a')
        for model in self.models:
            file.write(model.get_code())
            file.write("\n")
        file.close()

    def save_views(self):
        pass


class Project:
    project_name = setup_file.project_name
    user_model = setup_file.user_model

    def __init__(self):
        self.apps = list()
        for app in setup_file.apps.keys():
            self.apps.append(App(app))
        self.cmd = ProjectCommand(self.project_name)
        self.confs = ProjectConfigurations(self.project_name)
        self.timezone = None
        self.language = None
        self.use_token_auth = True
        try:
            self.timezone = setup_file.timezone
        except:
            pass
        try:
            self.language = setup_file.language
        except:
            pass
        try:
            self.use_token_auth = setup_file.user_model.use_token_auth
        except:
            pass

    def menu(self):
        print("0. Create a new venv")
        print("1. Create your project")
        option_choice = int(input("Type here: "))
        if (option_choice == 0):
            self.create_venv()
        elif (option_choice == 1):
            self.create_project()
            self.create_apps()
            self.register_apps()

    def create_venv(self):
        self.cmd.setup_venv()
        if platform.system() == "windows":
            print(
                "Type 'call myvenv/scripts/activate', re-execute the script and type 1!"
            )
            return
        print(
            "Type 'source myvenv/bin/activate', re-execute the script and type 1!"
        )

    def create_project(self):
        self.cmd.install_requirements()
        # setting up project
        self.cmd.start_project()
        self.confs.load_settings()
        self.confs.load_urls()
        self.confs.add_installed_modules()
        self.confs.set_cross_origin_all()
        self.confs.set_allowed_hosts_all()
        if self.use_token_auth == True:
            self.confs.add_token_login_model()
        if not self.timezone == None:
            self.confs.set_timezone(self.timezone)
        if not self.language == None:
            self.confs.set_language_code(self.language)

    def create_apps(self):
        for app in self.apps:
            self.cmd.create_app(app.name)

    def register_apps(self):
        for app in self.apps:
            app_name = app.name
            # add apps to confs and urls
            self.confs.add_module(app.name)
            self.confs.add_url_path(app.name)
            # register model spces to object
            models_name = setup_file.apps[app.name]['models'].keys()
            for model_name in models_name:
                model = Model(model_name)
                fields_name = setup_file.apps[
                    app.name]['models'][model_name].keys()
                for field_name in fields_name:
                    field_specs = setup_file.apps[
                        app.name]['models'][model_name][field_name]
                    field = Field(field_name, field_specs.get('template'),
                                  field_specs.get('field'),
                                  field_specs.get('options', list()),
                                  field_specs.get('serializers', {}))
                    model.add_field(field)
                app.add_model(model)
            # register view specs to object
            # for view_name in setup_file.apps[app.name]['views'].keys():
            #     view = setup_file.apps[app.name]['views'].get(view_name, None)
            #     app.add_view(
            #         View(
            #             view.get(view_name, view.get('template'),
            #                      view.get('options'), view.get('permissions'),
            #                      view.get('url_getters'))))
            app.save_models(self.project_name)
        # save changes
        self.confs.save_settings()
        self.confs.save_urls()


def main():
    project = Project()
    project.menu()


main()