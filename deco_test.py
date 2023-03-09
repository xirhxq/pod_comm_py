from time import sleep, time
import threading

class C:
    def timer(tol=1):
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time()
                result = func(*args, **kwargs)
                end_time = time()
                print(f'Time elap: {end_time - start_time:.2f}')
                if end_time - start_time < tol:
                    sleep(tol - end_time + start_time)
                print(f'Ended')
                return result
            return wrapper
        return decorator

    @timer(tol=2)
    def f(self):
        print('Hello')

    def spin(self):
        t_write = threading.Thread(target=self.f)
        t_write.start()

c = C()
c.spin()