**30.05.2022 - Heisenbug - Нагрузочное тестирование с помощью Python и Locust.**

**Чек лист для первого запуска теста:**
1. Установить Docker
2. Установить Python (для демонстрации на Heisenbug_2022 использовался Python 3.10.1)
3. Через командную строку открыть папку "./docker" из данного репозитория и выполнить команды:

      - docker-compose build
      - docker-compose up -d

3. После выполнения этих команд на вашей машине развернется четыре докер- контейнера:
      
      - kafka (localhost: 29092) - контейнер, содержащий в себе запущенное ПО Kafka с двумя топиками: "input-topic", "output-topic"
      - zookeeper (localhost:22181) - необходим для функционарования kafka
      - mock (localhost:9090) - содержит в себе запущенное веб приложение, которое принимает http запросы и отдаёт ответы на них
      - influxdb (localhost:8086 | login= username | password= passwordpasswordpassword) - рабочая версия InfluxDB, 
        в которую сохраняется время выполнения операций, запущенных по ходу теста
        
4. Перейти в папку "./demo_code" и выполнить команду для установки необходимых Python- модулей (команда зависит от ОС)
      
      - python3 -m pip install -r requirements.txt

**Запуск теста:**

- режим без интерфейса: locust -f locustfile.py --headless --html=locust_report.html
- режим с интерфейсом (localhost:8089): locust -f locustfile.py
- распределенный режим на одной машине: 

      - в терминале №1 выполнить: locust -f locustfile.py --master
      - в терминале №2,3 и т.д.: locust -f locustfile.py --worker --master-host=localhost
