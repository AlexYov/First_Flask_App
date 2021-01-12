import unittest
from datetime import datetime, timedelta
from app import application, db
from app.models import User, Post

class UserModelCase(unittest.TestCase): # класс тестирования функционала программы
    def setUp(self): # метод setUp запускается перед тестированием функционала
        application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all() # создаётся база банных (БД)
        
    def tearDown(self): # метод tearDown запускается после окончания тестирования
        db.session.remove() # удаляются данные из БД
        db.drop_all() # удаляется БД
        
    def test_password_hash(self): # метод по тестированию установки пароля и проверки хэш-функции
        user = User(username = 'sasha') # задаётся пользователь
        user.set_password('1234') # устанавливается пароль пользователю
        self.assertFalse(user.check_password('4321')) # проверка хэш-функции пароля. ответ должен быть False, так как пароль не является корректным
        self.assertTrue(user.check_password('1234')) # ответ должен быть True, так как пароль является корректным
        
    def test_follow(self): # метод по тестированию функционала пользователей: подписаться, отписаться
        user1 = User(username = 'sasha', email = 'sasha@yandex.ru') # задаётся пользователь
        user2 = User(username = 'rita', email = 'rita@yandex.ru')
        db.session.add_all([user1,user2]) # пользователи сохраняются в БД
        db.session.commit() # сохраняются изменения в БД
        self.assertEqual(user1.followed.all(), []) # проверка равенства двух значений: первое значение - подписки user1 (т.е. на кого подписан user1), второе значение - пустой список. так как user1 ни на кого не подписан, значит первое и второе значения равны.
        self.assertEqual(user1.followers.all(), []) # проверка равенства двух аргументов: первый - подписчики user1 (т.е. кто подписан на user1), второй - пустой список. так как никто не подписан на user1, значит первый и второй аргументы равны.
        self.assertEqual(user2.followed.all(), [])
        self.assertEqual(user2.followers.all(), [])
        
        user1.follow(user2) # user1 подписывается на user2
        db.session.commit()
        self.assertTrue(user1.is_following(user2)) # проверка подписан ли user1 на user2. ответ должен быть положительный
        self.assertFalse(user2.is_following(user1)) # проверка подписан ли user2 на user1. ответ должен быть отрицательный
        self.assertEqual(user1.followed.count(), 1) # проверка количества подписак у user1. ответ должен быть 1, так как он подписан только на user2
        self.assertEqual(user1.followed.first().username, 'rita') # проверка на кого подписан user1, т.е. user1 подписан на user2, а у user2 имя - rita, значит аргументы должны быть равны
        self.assertEqual(user2.followers.count(), 1) # проверка количества подписчиков у user2. ответ должен быть 1, так как на user2 подписан только user1
        self.assertEqual(user2.followers.first().username, 'sasha') 
        
        user1.unfollow(user2) # user1 отписывается от user2
        db.session.commit()
        self.assertFalse(user1.is_following(user2)) # проверка подписан ли user1 на user2. ответ должен быть отрицательный
        self.assertFalse(user2.is_following(user1))
        self.assertEqual(user1.followed.count(), 0) # проверка равенства двух аргументов. первый - количество подписок у user1, второй - 0. аргументы должны быть равны, так как user1 ни на кого не подписан
        self.assertEqual(user2.followers.count(), 0)
        
    def test_follow_posts(self): #
        #добавляем пользователей в базу данных
        user1 = User(username = 'sasha', email = 'sasha@yandex.ru')
        user2 = User(username = 'rita', email = 'rita@yandex.ru')
        user3 = User(username = 'slava', email = 'slava@yandex.ru')
        user4 = User(username = 'olya', email = 'olya@yandex.ru') 
        db.session.add_all([user1,user2,user3,user4]) 
        db.session.commit()
        
        # создаём записи постов пользователей
        post1 = Post(author = user1, body = f'post from user1 - {user1.username}', timestamp = datetime.now() + timedelta(seconds = 1))
        
        post2 = Post(author = user2, body = f'post from user2 - {user2.username}', timestamp = datetime.now() + timedelta(seconds = 1))
        
        post3 = Post(author = user3, body = f'post from user3 - {user3.username}', timestamp = datetime.now() + timedelta(seconds = 1))
        
        post4 = Post(author = user4, body = f'post from user4 - {user4.username}', timestamp = datetime.now() + timedelta(seconds = 1))
        
        db.session.add_all([post1, post2, post3, post4])
        db.session.commit()
        
        user1.follow(user2) # user1 подписан на user2
        user1.follow(user3) # user1 подписан на user3
        user2.follow(user4) # user2 подписан на user4
        user3.follow(user4) # user3 подписан на user4
        db.session.commit() 
        
        f1 = user1.followed_posts().all() # получаем все посты тех, на кого подписан user1
        f2 = user2.followed_posts().all()
        f3 = user3.followed_posts().all()
        f4 = user4.followed_posts().all() 
        self.assertAlmostEqual(f1, [post3, post2, post1]) # проверяем, что значения равны, а именно: переменная f1 должна равняться списку значений [post2, post3, post1], так как пользователь user1 подписан на пользователей user2 и user3, значит user1 должен получить все посты тех пользователей, на которых подписан, а также получить свои собственные посты
        self.assertEqual(f2, [post4, post2]) 
        self.assertEqual(f3, [post4, post3]) 
        self.assertEqual(f4, [post4])

if __name__ == '__main__':
    unittest.main(verbosity = 2) # запускаем тестирование и передаём аргумент verbosity = 2 для подробного вывода результата
