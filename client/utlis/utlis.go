package utlis

import (
	"bytes"
	"encoding/binary"
	"math"
	"reflect"
	"regexp"
	"strconv"
	"strings"
	"time"

	. "github.com/soulpower11/CZ4013-Project/const"
)

// IndexOfStringArr Get the index of a string in a string slice
func IndexOfStringArr(arr []string, str string) int {
	for pos, v := range arr {
		if v == str {
			return pos
		}
	}
	return -1
}

// StrToInt32 Convert string into int32
func StrToInt32(str string) int32 {
	hold, _ := strconv.ParseUint(strings.TrimSpace(str), 10, 32)
	hold32 := int32(hold)
	return hold32
}

// GetEndianness Will always return big endian
func GetEndianness() int32 {
	return int32(BigEndian)
}

// Functions to convert a variable type into byte array

func Int32ToBytes(num int32) ([]byte, int32) {
	_byte := make([]byte, 4)
	binary.BigEndian.PutUint32(_byte, uint32(num))
	return _byte, int32(len(_byte))
}

func Int32ToByte(num int32) []byte {
	_byte := make([]byte, 1)
	_byte[0] = byte(num & 0xFF)
	return _byte
}

func Float32ToBytes(num float32) ([]byte, int32) {
	_byte := make([]byte, 4)
	binary.BigEndian.PutUint32(_byte, math.Float32bits(num))
	return _byte, int32(len(_byte))
}

func StringToBytes(str string) ([]byte, int32) {
	return []byte(str), int32(len([]byte(str)))
}

func TimeToBytes(t time.Time) ([]byte, int32) {
	_byte := make([]byte, 8)
	binary.BigEndian.PutUint64(_byte, uint64(t.UnixNano()))
	return _byte, int32(len(_byte))
}

// ToBytes Takes in a variable and convert it into bytes
func ToBytes[T any](variable T) ([]byte, int32) {
	switch value := any(variable).(type) {
	case int32:
		return Int32ToBytes(value)
	case float32:
		return Float32ToBytes(value)
	case string:
		return StringToBytes(value)
	case time.Time:
		return TimeToBytes(value)
	}
	return nil, -1
}

// Functions to convert bytes back to its respective variable type

func BytesToInt32(_byte []byte, byteOrder int32) int32 {
	if byteOrder == int32(BigEndian) {
		return int32(binary.BigEndian.Uint32(_byte))
	} else {
		return int32(binary.LittleEndian.Uint32(_byte))
	}
}

func ByteToInt32(_byte []byte) int32 {
	return int32(_byte[0])
}

func BytesToFloat32(_byte []byte, byteOrder int32) float32 {
	if byteOrder == int32(BigEndian) {
		return math.Float32frombits(binary.BigEndian.Uint32(_byte))
	} else {
		return math.Float32frombits(binary.LittleEndian.Uint32(_byte))
	}
}

func BytesToString(_byte []byte) string {
	return string(bytes.Trim(_byte, "\x00"))
}

func BytesToTime(_byte []byte, byteOrder int32) time.Time {
	if byteOrder == int32(BigEndian) {
		return time.Unix(int64(binary.BigEndian.Uint64(_byte)), 0)
	} else {
		return time.Unix(int64(binary.LittleEndian.Uint64(_byte)), 0)
	}
}

// GetDataType Get the data type const of the variable
func GetDataType[T any](variable T) int32 {
	switch any(variable).(type) {
	case int32:
		return int32(IntType)
	case float32:
		return int32(FloatType)
	case string:
		return int32(StringType)
	case time.Time:
		return int32(TimeType)
	}
	return -1
}

// AddRequestID Add Request ID Bytes
// Contains a total of 23 Bytes
// IP 15 Bytes
// Time 8 Bytes
func AddRequestID(ip string, time time.Time, bytes []byte, size int32) ([]byte, int32) {
	resultBytes := make([]byte, 23+size)

	ipBytes, ipSize := ToBytes(ip)
	timeBytes, timeSize := ToBytes(time)

	copy(resultBytes[0:ipSize], ipBytes)
	if ipSize != int32(15) {
		padding := make([]byte, 15-ipSize)
		copy(resultBytes[ipSize:15], padding)
	}
	copy(resultBytes[15:15+timeSize], timeBytes)
	copy(resultBytes[23:23+size], bytes[:size])

	return resultBytes, 23 + size
}

// TurnPacketLossOff Turn off the packet loss byte from 1 to 0
func TurnPacketLossOff(bytes_ []byte) []byte {
	packetLossBytes := Int32ToByte(0)

	copy(bytes_[27:28], packetLossBytes)
	return bytes_
}

// AddRequestHeader Add the Request Header Bytes
// Contains a total of 9 Bytes
// Service Type 1 Byte
// Message Type 1 Byte
// Byte Ordering 1 Byte
// Error Code 1 Byte
// Packet Loss 1 Byte
// No. of element 4 Bytes
func AddRequestHeader(serviceType, messageType, errorCode, packetLoss, noOfElement int32, bytes []byte, size int32) ([]byte, int32) {
	resultBytes := make([]byte, 9+size)

	serviceBytes := Int32ToByte(serviceType)
	messageBytes := Int32ToByte(messageType)
	byteOrderingBytes := Int32ToByte(GetEndianness())
	errorCodeBytes := Int32ToByte(errorCode)
	packetLossBytes := Int32ToByte(packetLoss)
	noOfElementBytes, noOfElementSize := ToBytes(noOfElement)

	copy(resultBytes[0:1], serviceBytes)
	copy(resultBytes[1:2], messageBytes)
	copy(resultBytes[2:3], byteOrderingBytes)
	copy(resultBytes[3:4], errorCodeBytes)
	copy(resultBytes[4:5], packetLossBytes)
	copy(resultBytes[5:5+noOfElementSize], noOfElementBytes)
	copy(resultBytes[9:9+size], bytes[:size])

	return resultBytes, 9 + size
}

// AddElementHeader Add the Element Header Bytes
// Contain a total of 4 Bytes
// Length of Element 4 Bytes
func AddElementHeader(length int32, bytes []byte, size int32) ([]byte, int32) {
	resultBytes := make([]byte, 4+size)

	lengthBytes, lengthSize := ToBytes(length)

	copy(resultBytes[0:0+lengthSize], lengthBytes)
	copy(resultBytes[4:4+size], bytes[:size])

	return resultBytes, 4 + size
}

// AddVariableHeader Add the Variable Header Bytes
// Contain a total of 5 Bytes
// Data Type 1 Bytes
// Length of variable 4 Bytes
func AddVariableHeader(dataType, length int32, bytes []byte, size int32) ([]byte, int32) {
	resultBytes := make([]byte, 5+size)

	dataTypeBytes := Int32ToByte(dataType)
	lengthBytes, lengthSize := ToBytes(length)

	copy(resultBytes[0:1], dataTypeBytes)
	copy(resultBytes[1:1+lengthSize], lengthBytes)
	copy(resultBytes[5:5+size], bytes[:size])

	return resultBytes, 5 + size
}

// SetField Set the variable to the respective field
func SetField(dataClass interface{}, index int32, value interface{}, serviceType, messageType int32) interface{} {
	switch {
	case serviceType == int32(QueryFlightId_) && messageType == int32(Request):
		dataStruct, _ := dataClass.(QueryFlightIdRequest)
		switch index {
		case 0:
			dataStruct.Source = value.(string)
			dataClass = dataStruct
			break
		case 1:
			dataStruct.Destination = value.(string)
			dataClass = dataStruct
			break
		}
	case serviceType == int32(QueryFlightId_) && messageType == int32(Reply):
		dataStruct, _ := dataClass.(QueryFlightIdResponse)
		switch index {
		case 0:
			dataStruct.FlightId = value.(int32)
			dataClass = dataStruct
			break
		}
	case serviceType == int32(QueryDepartureTime_) && messageType == int32(Request):
		dataStruct, _ := dataClass.(QueryDepartureTimeRequest)
		switch index {
		case 0:
			dataStruct.FlightId = value.(int32)
			dataClass = dataStruct
			break
		}
	case serviceType == int32(QueryDepartureTime_) && messageType == int32(Reply):
		dataStruct, _ := dataClass.(QueryDepartureTimeResponse)
		switch index {
		case 0:
			dataStruct.DepartureTime = value.(time.Time)
			dataClass = dataStruct
			break
		case 1:
			dataStruct.AirFare = value.(float32)
			dataClass = dataStruct
			break
		case 2:
			dataStruct.SeatAvailability = value.(int32)
			dataClass = dataStruct
			break
		}
	case serviceType == int32(Reservation_) && messageType == int32(Request):
		dataStruct, _ := dataClass.(ReservationRequest)
		switch index {
		case 0:
			dataStruct.FlightId = value.(int32)
			dataClass = dataStruct
			break
		case 1:
			dataStruct.NoOfSeats = value.(int32)
			dataClass = dataStruct
			break
		}
	case serviceType == int32(Reservation_) && messageType == int32(Reply):
		dataStruct, _ := dataClass.(ReservationResponse)
		switch index {
		case 0:
			dataStruct.Msg = value.(string)
			dataClass = dataStruct
			break
		}
	case serviceType == int32(Monitor_) && messageType == int32(Request):
		dataStruct, _ := dataClass.(MonitorRequest)
		switch index {
		case 0:
			dataStruct.FlightId = value.(int32)
			dataClass = dataStruct
			break
		case 1:
			dataStruct.MonitorInterval = value.(int32)
			dataClass = dataStruct
			break
		}
	case serviceType == int32(Monitor_) && messageType == int32(Reply):
		dataStruct, _ := dataClass.(MonitorResponse)
		switch index {
		case 0:
			dataStruct.Msg = value.(string)
			dataClass = dataStruct
			break
		}
	case serviceType == int32(CheckReservation_) && messageType == int32(Request):
		dataStruct, _ := dataClass.(CheckReservationRequest)
		switch index {
		case 0:
			dataStruct.FlightId = value.(int32)
			dataClass = dataStruct
			break
		}
	case serviceType == int32(CheckReservation_) && messageType == int32(Reply):
		dataStruct, _ := dataClass.(CheckReservationResponse)
		switch index {
		case 0:
			dataStruct.SeatsReserved = value.(int32)
			dataClass = dataStruct
			break
		}
	case serviceType == int32(Cancellation_) && messageType == int32(Request):
		dataStruct, _ := dataClass.(CancellationRequest)
		switch index {
		case 0:
			dataStruct.FlightId = value.(int32)
			dataClass = dataStruct
			break
		}
	case serviceType == int32(Cancellation_) && messageType == int32(Reply):
		dataStruct, _ := dataClass.(CancellationResponse)
		switch index {
		case 0:
			dataStruct.Msg = value.(string)
			dataClass = dataStruct
			break
		}
	}
	return dataClass
}

// DecodeIPFromRequestId Decode the IP address from the Request ID
func DecodeIPFromRequestId(requestId []byte) string {
	ip := BytesToString(requestId[0:15])
	re := regexp.MustCompile(`[^.\d]+`)

	return re.ReplaceAllString(ip, "")
}

// DecodeRequestHeader Decode the Request Header Bytes
func DecodeRequestHeader(requestHeader []byte) (int32, int32, int32, int32, int32, int32) {
	byteOrdering := ByteToInt32(requestHeader[2:3])
	serviceType := ByteToInt32(requestHeader[0:1])
	messageType := ByteToInt32(requestHeader[1:2])
	errorCode := ByteToInt32(requestHeader[3:4])
	packetLoss := ByteToInt32(requestHeader[4:5])
	noOfElement := BytesToInt32(requestHeader[5:], byteOrdering)

	return byteOrdering, serviceType, messageType, errorCode, packetLoss, noOfElement
}

// DecodeElementHeader Decode the Element Header Bytes
func DecodeElementHeader(elementsByte []byte, byteOrdering int32) (int32, []byte) {
	lengthOfElement := BytesToInt32(elementsByte[:4], byteOrdering)
	variablesByte := elementsByte[4 : 4+lengthOfElement]

	return lengthOfElement, variablesByte
}

// DecodeVariableHeader Decode the Variable Header Bytes
func DecodeVariableHeader(variableHeader []byte, byteOrdering int32) (int32, int32) {
	dataType := ByteToInt32(variableHeader[0:1])
	lengthOfVariable := BytesToInt32(variableHeader[1:], byteOrdering)

	return dataType, lengthOfVariable
}

// DecodeQuery Decode the bytes into each struct fields
func DecodeQuery(query []interface{}, elementsByte []byte, byteOrdering, noOfElement, serviceType, messageType int32) []interface{} {
	for i := 0; i < int(noOfElement); i++ {
		lengthOfElement, variablesByte := DecodeElementHeader(elementsByte, byteOrdering)
		elementsByte = elementsByte[4+lengthOfElement:]

		index := int32(0)
		for len(variablesByte) != 0 {
			variableHeader := variablesByte[:5]
			dataType, lengthOfVariable := DecodeVariableHeader(variableHeader, byteOrdering)

			variableByte := variablesByte[5 : 5+lengthOfVariable]

			switch dataType {
			case int32(IntType):
				query[i] = SetField(
					query[i],
					index,
					BytesToInt32(variableByte, byteOrdering),
					serviceType,
					messageType,
				)
				break
			case int32(FloatType):
				query[i] = SetField(
					query[i],
					index,
					BytesToFloat32(variableByte, byteOrdering),
					serviceType,
					messageType,
				)
				break
			case int32(StringType):
				query[i] = SetField(
					query[i],
					index,
					BytesToString(variableByte),
					serviceType,
					messageType,
				)
				break
			case int32(TimeType):
				query[i] = SetField(
					query[i],
					index,
					BytesToTime(variableByte, byteOrdering),
					serviceType,
					messageType,
				)
				break
			}

			variablesByte = variablesByte[5+lengthOfVariable:]
			index += 1
		}
	}

	return query
}

// DecodeError Decode the error message from bytes
func DecodeError(queryResponse Response, elementsByte []byte, byteOrdering int32) Response {
	lengthOfElement, variablesByte := DecodeElementHeader(elementsByte, byteOrdering)
	elementsByte = elementsByte[4+lengthOfElement:]

	variableHeader := variablesByte[:5]
	_, lengthOfVariable := DecodeVariableHeader(variableHeader, byteOrdering)
	variableByte := variablesByte[5 : 5+lengthOfVariable]

	queryResponse.Error = BytesToString(variableByte)

	return queryResponse
}

// Unmarshal The unmarshal function to unmarshal the bytes into struct. Containing
// 8 Bytes Request Header
// 4 Bytes Element Header per element in an array
// 5 Bytes Variable Header per variable in an element
func Unmarshal(bytesStr []byte) (queryRequest []interface{}, queryResponse Response, serviceType, errorCode, packetLoss int32) {
	requestHeader := bytesStr[:9]
	byteOrdering, serviceType, messageType, errorCode, packetLoss, noOfElement := DecodeRequestHeader(requestHeader)

	elementsByte := bytesStr[9:]

	if errorCode != 0 && messageType == int32(Reply) {
		queryResponse = DecodeError(queryResponse, elementsByte, byteOrdering)
		return nil, queryResponse, serviceType, errorCode, packetLoss
	}

	if messageType == int32(Request) {
		switch serviceType {
		case int32(QueryFlightId_):
			queryRequest = make([]interface{}, noOfElement)
			for i := range queryRequest {
				queryRequest[i] = QueryFlightIdRequest{}
			}
			break
		case int32(QueryDepartureTime_):
			queryRequest = make([]interface{}, noOfElement)
			for i := range queryRequest {
				queryRequest[i] = QueryDepartureTimeRequest{}
			}
			break
		case int32(Reservation_):
			queryRequest = make([]interface{}, noOfElement)
			for i := range queryRequest {
				queryRequest[i] = ReservationRequest{}
			}
			break
		case int32(Monitor_):
			queryRequest = make([]interface{}, noOfElement)
			for i := range queryRequest {
				queryRequest[i] = MonitorRequest{}
			}
			break
		case int32(CheckReservation_):
			queryRequest = make([]interface{}, noOfElement)
			for i := range queryRequest {
				queryRequest[i] = CheckReservationRequest{}
			}
			break
		case int32(Cancellation_):
			queryRequest = make([]interface{}, noOfElement)
			for i := range queryRequest {
				queryRequest[i] = CancellationRequest{}
			}
			break
		}

		queryRequest = DecodeQuery(
			queryRequest,
			elementsByte,
			byteOrdering,
			noOfElement,
			serviceType,
			messageType,
		)

		return queryRequest, Response{}, serviceType, errorCode, packetLoss
	} else if messageType == int32(Reply) {
		switch serviceType {
		case int32(QueryFlightId_):
			queryResponse.Value = make([]interface{}, noOfElement)
			for i := range queryResponse.Value {
				queryResponse.Value[i] = QueryFlightIdResponse{}
			}
			break
		case int32(QueryDepartureTime_):
			queryResponse.Value = make([]interface{}, noOfElement)
			for i := range queryResponse.Value {
				queryResponse.Value[i] = QueryDepartureTimeResponse{}
			}
			break
		case int32(Reservation_):
			queryResponse.Value = make([]interface{}, noOfElement)
			for i := range queryResponse.Value {
				queryResponse.Value[i] = ReservationResponse{}
			}
			break
		case int32(Monitor_):
			queryResponse.Value = make([]interface{}, noOfElement)
			for i := range queryResponse.Value {
				queryResponse.Value[i] = MonitorResponse{}
			}
			break
		case int32(CheckReservation_):
			queryResponse.Value = make([]interface{}, noOfElement)
			for i := range queryResponse.Value {
				queryResponse.Value[i] = CheckReservationResponse{}
			}
			break
		case int32(Cancellation_):
			queryResponse.Value = make([]interface{}, noOfElement)
			for i := range queryResponse.Value {
				queryResponse.Value[i] = CancellationResponse{}
			}
			break
		}

		queryResponse.Value = DecodeQuery(
			queryResponse.Value,
			elementsByte,
			byteOrdering,
			noOfElement,
			serviceType,
			messageType,
		)

		return nil, queryResponse, serviceType, errorCode, packetLoss
	}
	return nil, Response{}, serviceType, errorCode, packetLoss
}

// Marshal The marshaling function
// Marshal the struct into bytes
func Marshal(r interface{}, serviceType, messageType, errorCode, packetLoss int32) ([]byte, int32) {
	length := int32(1)
	resultSize := int32(0)
	var resultBytes []byte

	if errorCode != 0 && messageType == int32(Reply) {
		errorBytes, errorSize := ToBytes(r.(*Response).Error)
		errorBytes, errorSize = AddVariableHeader(int32(StringType), errorSize, errorBytes, errorSize)
		errorBytes, errorSize = AddElementHeader(errorSize, errorBytes, errorSize)

		resultSize += errorSize
		resultBytes = append(resultBytes, errorBytes...)
		RequestHeaderBytes, size := AddRequestHeader(
			serviceType, messageType, errorCode, packetLoss, length, resultBytes, resultSize,
		)
		return RequestHeaderBytes, size
	}

	if messageType == int32(Request) {
		tempSize := int32(0)
		var tempBytes []byte

		dataFields := r

		v := reflect.ValueOf(dataFields)

		for i := 0; i < v.NumField(); i++ {
			fieldBytes, fieldSize := ToBytes(v.Field(i).Interface())
			fieldBytes, fieldSize = AddVariableHeader(
				GetDataType(v.Field(i).Interface()), fieldSize, fieldBytes, fieldSize,
			)
			tempBytes = append(tempBytes, fieldBytes...)
			tempSize += fieldSize
		}

		tempBytes, tempSize = AddElementHeader(tempSize, tempBytes, tempSize)

		resultSize += tempSize
		resultBytes = append(resultBytes, tempBytes...)
	} else if messageType == int32(Reply) {
		length = int32(len(r.(*Response).Value))

		for _, dataFields := range r.(*Response).Value {
			tempSize := int32(0)
			var tempBytes []byte

			v := reflect.ValueOf(dataFields)

			for i := 0; i < v.NumField(); i++ {
				fieldBytes, fieldSize := ToBytes(v.Field(i).Interface())
				fieldBytes, fieldSize = AddVariableHeader(
					GetDataType(v.Field(i).Interface()), fieldSize, fieldBytes, fieldSize,
				)
				tempBytes = append(tempBytes, fieldBytes...)
				tempSize += fieldSize
			}

			resultSize += tempSize
			resultBytes = append(resultBytes, tempBytes...)
		}
	}

	marshalledBytes, size := AddRequestHeader(
		serviceType, messageType, errorCode, packetLoss, length, resultBytes, resultSize,
	)
	return marshalledBytes, size
}
