import os
import shutil
import zipfile
import configparser

class FileManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.root_dir = os.path.abspath(self.config["DEFAULT"].get("work_dir", "./workspace"))
        os.makedirs(self.root_dir, exist_ok=True)
        self.user_dir = None

    def register_user(self, username):
        user_path = os.path.join(self.root_dir, username)
        os.makedirs(user_path, exist_ok=True)
        self.user_dir = os.path.abspath(user_path)
        os.chdir(self.user_dir)
        print(f"Пользователь '{username}' зарегистрирован. Рабочая директория: {self.user_dir}")

    def _abs_path(self, name):
        return os.path.abspath(os.path.join(os.getcwd(), name))

    def _is_inside_user(self, path):
        return os.path.commonpath([self.user_dir, path]) == self.user_dir

    def _check_access(self, path):
        if not self._is_inside_user(path):
            raise PermissionError("Доступ за пределы пользовательской директории запрещён.")

    def create_dir(self, name):
        path = self._abs_path(name)
        self._check_access(path)
        os.makedirs(path, exist_ok=True)
        print(f"Папка '{name}' создана.")

    def delete_dir(self, name):
        path = self._abs_path(name)
        self._check_access(path)
        shutil.rmtree(path)
        print(f"Папка '{name}' удалена.")

    def list_dir(self):
        print(f"\nСодержимое {os.getcwd()}:")
        for item in os.listdir():
            marker = "[DIR]" if os.path.isdir(item) else "     "
            print(f"{marker} {item}")

    def change_dir(self, name):
        path = self._abs_path(name)
        self._check_access(path)
        if os.path.isdir(path):
            os.chdir(path)
            print(f"Переход в: {path}")
        else:
            print("Директория не найдена.")

    def create_file(self, name):
        path = self._abs_path(name)
        self._check_access(path)
        open(path, 'x').close()
        print(f"Файл '{name}' создан.")

    def read_file(self, name):
        path = self._abs_path(name)
        self._check_access(path)
        with open(path, 'r', encoding='utf-8') as f:
            print(f.read())

    def write_file(self, name, *text):
        path = self._abs_path(name)
        self._check_access(path)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(' '.join(text) + '\n')
        print(f"Запись в файл '{name}' выполнена.")

    def delete_file(self, name):
        path = self._abs_path(name)
        self._check_access(path)
        os.remove(path)
        print(f"Файл '{name}' удалён.")

    def copy_file(self, src, dst):
        src_path = self._abs_path(src)
        dst_path = self._abs_path(dst)
        self._check_access(src_path)
        self._check_access(dst_path)
        shutil.copy2(src_path, dst_path)
        print(f"Файл '{src}' скопирован в '{dst}'.")

    def move_file(self, src, dst):
        src_path = self._abs_path(src)
        dst_path = self._abs_path(dst)
        self._check_access(src_path)
        self._check_access(dst_path)
        shutil.move(src_path, dst_path)
        print(f"Файл '{src}' перемещён в '{dst}'.")

    def rename_file(self, old, new):
        self.move_file(old, new)

    def archive(self, source, dest_name):
        src_path = self._abs_path(source)
        dest_path = self._abs_path(dest_name)
        self._check_access(src_path)
        shutil.make_archive(dest_path, 'zip', src_path)
        print(f"Архив '{dest_name}.zip' создан.")

    def extract(self, zip_path, dest_dir):
        z_path = self._abs_path(zip_path)
        d_path = self._abs_path(dest_dir)
        self._check_access(z_path)
        self._check_access(d_path)
        with zipfile.ZipFile(z_path, 'r') as zip_ref:
            zip_ref.extractall(d_path)
        print(f"Архив '{zip_path}' распакован в '{dest_dir}'.")

    def quota(self):
        total, used, free = shutil.disk_usage(self.user_dir)
        print("\nИнформация о дисковом пространстве:")
        print(f"  Всего: {total // (1024**2)} MB")
        print(f"  Использовано: {used // (1024**2)} MB")
        print(f"  Свободно: {free // (1024**2)} MB")
        if used / total > 0.9:
            print("Внимание: диск почти заполнен!")

def main():
    fm = FileManager()

    commands = {
        "register": fm.register_user,
        "ls": fm.list_dir,
        "cd": fm.change_dir,
        "mkdir": fm.create_dir,
        "rmdir": fm.delete_dir,
        "touch": fm.create_file,
        "read": fm.read_file,
        "write": fm.write_file,
        "rm": fm.delete_file,
        "cp": fm.copy_file,
        "mv": fm.move_file,
        "rename": fm.rename_file,
        "zip": fm.archive,
        "unzip": fm.extract,
        "quota": fm.quota,
        "help": lambda: print_help(),
        "exit": lambda: exit()
    }

    def print_help():
        print("""
Список команд:
  register <username>       — регистрация пользователя
  ls                        — показать содержимое
  cd <dir>                  — перейти в папку
  mkdir <name>              — создать папку
  rmdir <name>              — удалить папку
  touch <file>              — создать файл
  read <file>               — прочитать файл
  write <file> <text>       — записать в файл
  rm <file>                 — удалить файл
  cp <src> <dst>            — копировать файл
  mv <src> <dst>            — переместить файл
  rename <old> <new>        — переименовать файл
  zip <src> <name>          — архивировать папку/файл
  unzip <zip> <dst>         — распаковать архив
  quota                     — информация о диске
  help                      — справка
  exit                      — выход
""")

    print("Перед началом работы зарегистрируйте пользователя командой: register <username>")
    while True:
        try:
            command = input("> ").strip().split()
            if not command:
                continue
            cmd, *args = command
            if cmd not in commands:
                print("Неизвестная команда.")
                continue
            if cmd != "register" and fm.user_dir is None:
                print("Сначала выполните регистрацию пользователя.")
                continue
            commands[cmd](*args)
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
