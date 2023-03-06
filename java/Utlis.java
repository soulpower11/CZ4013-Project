import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.time.Instant;

public class Utlis {
    public static int getEndianness() {
        ByteOrder order = ByteOrder.nativeOrder();
        if (order.equals(ByteOrder.BIG_ENDIAN)) {
            return Enums.ByteOrdering.BIG_ENDIAN.getValue();
        } else {
            return Enums.ByteOrdering.LITTLE_ENDIAN.getValue();
        }
    }

    public static byte[] intToBytes(int num) {
        byte[] bytes = new byte[4];
        ByteBuffer.wrap(bytes).putInt(num);

        return bytes;
    }

    public static byte[] floatToBytes(Float num) {
        byte[] bytes = new byte[4];
        ByteBuffer.wrap(bytes).putFloat(num);

        return bytes;
    }

    public static byte[] stringToBytes(String string) {
        return string.getBytes(StandardCharsets.US_ASCII);
    }

    public static byte[] timeToBytes(Instant time) {
        byte[] bytes = new byte[8];
        long epochMillis = time.toEpochMilli();
        ByteBuffer.wrap(bytes).putLong(epochMillis);

        return bytes;
    }

}
