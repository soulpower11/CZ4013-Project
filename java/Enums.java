public class Enums {
    public enum DataType {
        INT_TYPE(0),
        FLOAT_TYPE(1),
        STRING_TYPE(2),
        TIME_TYPE(3);

        private final int value;

        DataType(final int newValue) {
            value = newValue;
        }

        public int getValue() {
            return value;
        }
    }

    public enum ServiceType {
        QUERY_FLIGHTID(0),
        QUERY_DEPARTURETIME(1),
        RESERVATION(2),
        MONITOR(3),
        CHECK_ARRIVALTIME(4),
        CANCALLATION(5);

        private final int value;

        ServiceType(final int newValue) {
            value = newValue;
        }

        public int getValue() {
            return value;
        }
    }

    public enum MessageType {
        REQUEST(0),
        REPLY(1);

        private final int value;

        MessageType(final int newValue) {
            value = newValue;
        }

        public int getValue() {
            return value;
        }
    }

    public enum ByteOrdering {
        BIG_ENDIAN(0),
        LITTLE_ENDIAN(1);

        private final int value;

        ByteOrdering(final int newValue) {
            value = newValue;
        }

        public int getValue() {
            return value;
        }
    }
}
