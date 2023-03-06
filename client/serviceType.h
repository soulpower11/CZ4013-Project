#include <time.h>

typedef enum DataType
{
    INT_TYPE,
    FLOAT_TYPE,
    STRING_TYPE,
    TIME_TYPE,
} DataType;

typedef enum ServiceType
{
    QUERY_FLIGHTID,
    QUERY_DEPARTURETIME,
    RESERVATION,
    MONITOR,
    CHECK_ARRIVALTIME,
    CANCALLATION,
} ServiceType;

typedef enum MessageType
{
    REQUEST,
    REPLY,
} MessageType;

typedef enum ByteOrdering
{
    BIG_ENDIAN,
    LITTLE_ENDIAN,
} ByteOrdering;

typedef struct QueryFlightIdRequest
{
    char *source;
    char *destination;
} QueryFlightIdRequest;

typedef struct QueryFlightIdResponse
{
    int flightId;
} QueryFlightIdResponse;

typedef struct QueryDepartureTimeRequest
{
    int flightId;
} QueryDepartureTimeRequest;

typedef struct QueryDepartureTimeResponse
{
    time_t departureTime;
    float airFare;
    int seatAvailability;
} QueryDepartureTimeResponse;

typedef struct ReservationRequest
{
    int flightId;
    int noOfSeats;
} ReservationRequest;

typedef struct ReservationResponse
{
    char *msg;
} ReservationResponse;

typedef struct MonitorRequest
{
    int flightId;
    int monitorInterval;
} MonitorRequest;

typedef struct MonitorResponse
{
    char *msg;
} MonitorResponse;

typedef struct CheckArrivalTimeRequest
{
    int flightId;
} CheckArrivalTimeRequest;

typedef struct CheckArrivalTimeResponse
{
    time_t arrivalTime;
} CheckArrivalTimeResponse;

typedef struct CancellationRequest
{
    int flightId;
} CancellationRequest;

typedef struct CancellationResponse
{
    char *msg;
} CancellationResponse;

typedef union ResponseValue
{
    struct QueryFlightIdResponse *qfi;
    struct QueryDepartureTimeResponse *qdt;
    struct ReservationResponse *r;
    struct MonitorResponse *m;
    struct CheckArrivalTimeResponse *cat;
    struct CancellationResponse *c;
} ResponseValue;

typedef struct Response
{
    ResponseValue value;
    char *error;
} Response;

typedef union RequestValue
{
    struct QueryFlightIdRequest *qfi;
    struct QueryDepartureTimeRequest *qdt;
    struct ReservationRequest *r;
    struct MonitorRequest *m;
    struct CheckArrivalTimeRequest *cat;
    struct CancellationRequest *c;
    struct Response res;
} RequestValue;

typedef struct Message
{
    ServiceType sType;
    MessageType mType;
    RequestValue value;
    int length;
} Message;
