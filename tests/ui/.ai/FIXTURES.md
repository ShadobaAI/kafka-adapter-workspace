# UI test fixtures and initialization

Read this before initializing a test infobase or using or changing prepared test data. The procedures below belong to the `examples` extension's `кфк_т_ТестовыеДанные` common module.

For every new test infobase, call these procedures in order:

```bsl
кфк_т_ТестовыеДанные.ИнициализацияДанных();
кфк_т_ТестовыеДанные.ИнициализацияПользователей();
```

## Data initialization

`ИнициализацияДанных()` enables `кфкИспользоватьИнтеграцию` and `кфкИспользоватьПотоковыйРежим`. It creates or updates `Брокер по умолчанию`, enables `localhost:29091` and `localhost:29092`, disables `localhost:29093`, and clears connection parameters. It creates one `Диспетчер задач` group in each of the producer and consumer catalogs, with two processing threads and one transport thread. Each item below belongs to its corresponding group and uses the default broker.

| Items | Metadata | Topic |
| --- | --- | --- |
| `Продюсер: ТестовыйСправочник`, `Консьюмер: ТестовыйСправочник` | `Справочник.кфк_т_ТестовыйСправочник` | `1c.test-catalogs` |
| `Продюсер: ТестовыйДокумент`, `Консьюмер: ТестовыйДокумент` | `Документ.кфк_т_ТестовыйДокумент` | `1c.test-documents` |
| `Продюсер: Тестовый РС`, `Консьюмер: Тестовый РС` | `РегистрСведений.кфк_т_ТестовыйРегистрСведений` | `1c.test-information-registers` |
| `Продюсер: Тестовый РС (ПР)` | `РегистрСведений.кфк_т_ТестовыйРегистрСведенийПР` | `1c.test-information-registers-pr` |
| `Продюсер: Тестовый РН` | `РегистрНакопления.кфк_т_ТестовыйРегистрНакопления` | `1c.test-accumulation-registers` |

It also creates `Продюсер: Общий`, configured for all five metadata objects with registration, serialization and publication locked, and `Консьюмер: Общий`, configured for three topics with reading and deserialization locked. The full set contains one broker, two groups, six producers and four consumers.

The procedure creates exchange settings, not the test catalog items, documents or register records themselves. Exported accessors include `СсылкаБрокераПоУмолчанию()`, `СсылкаГруппыПродюсеров()`, `СсылкаГруппыКонсьюмеров()` and accessors for individual producers and consumers.

Calling it again updates fixed references and repopulates table parts across the entire set. Do not use it as cleanup for one item or as a guarantee of a full rollback.

## User initialization

`ИнициализацияПользователей()` creates an administrator through BSP, copies its properties for `АдминистраторТакси`, applies initial settings for that user, and creates the two Kafka users with the roles in [AGENTS.md](../AGENTS.md). It allows external reports and data processors, disables dangerous-action and security warnings for prepared users, and clears the `Служебный` flag on all linked `Пользователи` catalog items that have it.

Both Kafka users also receive `кфк_т_ДобавлениеИзменениеТестовыхДанных` for the `examples` extension and common client-start and BSP roles. This does not grant Kafka subsystem administration rights.
