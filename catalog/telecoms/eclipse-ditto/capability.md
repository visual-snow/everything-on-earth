# Sandbox Capabilities

Eclipse Ditto is an open-source IoT framework that implements the digital twins pattern, providing virtual representations of physical devices accessible over standard messaging and REST interfaces. It manages device state, access control, and search across a fleet of connected things using a microservices architecture. It does not include a built-in message broker, time-series storage, or device drivers — external protocol infrastructure must be supplied separately.

## Digital Twin Management
- Things can be created, read, updated, and deleted as virtual device representations.
- Each thing carries attributes (device metadata) and features (sensor readings, actuator state).
- Change events are emitted whenever a thing's state is modified.

## Access Control
- Policies define which subjects can perform which actions on which resources.
- Permissions can be scoped to individual things, feature groups, or attribute paths.
- Policy enforcement is applied consistently across all API entry points.

## Search and Query
- Things can be queried by attribute values, feature properties, and policy subjects.
- Search results are paginated and can be filtered with RQL expressions.

## Connectivity
- Things receive and push state updates over MQTT, AMQP, Kafka, and HTTP channels.
- Each connectivity channel has an independently monitored connection status.
- W3C Web of Things (WoT) descriptions can be associated with things for interoperability.

## Configuration
- Authentication can be configured via JWT tokens or basic auth depending on the deployment mode.
- Connectivity targets (external brokers, Kafka clusters) are defined per channel.
- Log verbosity and JVM memory allocation are tunable per microservice.

## Constraints
- MongoDB is the only supported persistence backend — no alternative database is documented.
- No built-in message broker is included; an external MQTT broker, AMQP endpoint, or Kafka cluster must be provisioned separately for device connectivity.
- No time-series storage is provided — only the current state of each thing is persisted, not its history.
- The default single-instance deployment is not configured for high availability or horizontal scaling.
- No built-in observability pipeline — there is no metrics dashboard or alerting stack included.
