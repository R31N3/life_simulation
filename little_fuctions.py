def timer(executable_function):  # декоратор, честно скопированный с habrahabr.ru и чуток доделанный
    import time

    def decorate(*args, **kwargs):
        time_point = time.time()
        result = executable_function(*args, **kwargs)
        print('Время выполнения функции "{}": {:f} секунд'
              .format(executable_function.__name__, time.time() - time_point))
        return result
    return decorate


def smart_timeout(timeout: int = 0.34):
    import time

    def wrap(executable_function):
        def decorate(*args, **kwargs):
            start_time = time.time()
            result = executable_function(*args, **kwargs)
            if time.time() - start_time < timeout:
                time.sleep(timeout - (time.time() - start_time))
            return result
        return decorate
    return wrap


def error_protection(executable_function):
    import time

    def decorate(*args, **kwargs):
        try:
            result = executable_function(*args, **kwargs)
        except Exception as exc:
            print("==========\nError:\n{}\nDate: {}\n=========="
                  .format(exc, time.strftime("%H.%M.%S - %d.%m.%Y", time.localtime())))
        else:
            return result
    return decorate
