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

	. "github.com/soulpower11/CZ4031-Project/const"
)

func StrToInt32(str string) int32 {
	hold, _ := strconv.ParseUint(strings.TrimSpace(str), 10, 32)
	hold32 := int32(hold)
	return hold32
}

// Always use big endian
func GetEndianness() int32 {
	return int32(BIG_ENDIAN)
}

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

func StringToBytes(s string) ([]byte, int32) {
	return []byte(s), int32(len([]byte(s)))
}

func TimeToBytes(t time.Time) ([]byte, int32) {
	_byte := make([]byte, 8)
	binary.BigEndian.PutUint64(_byte, uint64(t.UnixNano()))
	return _byte, int32(len(_byte))
}

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

func BytesToInt32(_byte []byte, byteOrder int32) int32 {
	if byteOrder == int32(BIG_ENDIAN) {
		return int32(binary.BigEndian.Uint32(_byte))
	} else {
		return int32(binary.LittleEndian.Uint32(_byte))
	}
}

func ByteToInt32(_byte []byte) int32 {
	return int32(_byte[0])
}

func BytesToFloat32(_byte []byte, byteOrder int32) float32 {
	if byteOrder == int32(BIG_ENDIAN) {
		return math.Float32frombits(binary.BigEndian.Uint32(_byte))
	} else {
		return math.Float32frombits(binary.LittleEndian.Uint32(_byte))
	}
}

func BytesToString(_byte []byte) string {
	return string(bytes.Trim(_byte, "\x00"))
}

func BytesToTime(_byte []byte, byteOrder int32) time.Time {
	if byteOrder == int32(BIG_ENDIAN) {
		return time.Unix(int64(binary.BigEndian.Uint64(_byte)), 0)
	} else {
		return time.Unix(int64(binary.LittleEndian.Uint64(_byte)), 0)
	}
}

func GetDataType[T any](variable T) int32 {
	switch any(variable).(type) {
	case int32:
		return int32(INT_TYPE)
	case float32:
		return int32(FLOAT_TYPE)
	case string:
		return int32(STRING_TYPE)
	case time.Time:
		return int32(TIME_TYPE)
	}
	return -1
}

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

func TurnTimeOutOff(bytes_ []byte) []byte {
	timeOutBytes := Int32ToByte(0)

	copy(bytes_[27:28], timeOutBytes)
	return bytes_
}

// Service Type 1 Byte
// Message Type 1 Byte
// Byte Ordering 1 Byte
// Error Code 1 Byte
// Time Out 1 Byte
// No. of element 4 Byte
func AddRequestHeader(serviceType, messageType, errorCode, timeOut, noOfElement int32, bytes []byte, size int32) ([]byte, int32) {
	resultBytes := make([]byte, 9+size)

	serviceBytes := Int32ToByte(serviceType)
	messageBytes := Int32ToByte(messageType)
	byteOrderingBytes := Int32ToByte(GetEndianness())
	errorCodeBytes := Int32ToByte(errorCode)
	timeOutBytes := Int32ToByte(timeOut)
	noOfElementBytes, noOfElementSize := ToBytes(noOfElement)

	copy(resultBytes[0:1], serviceBytes)
	copy(resultBytes[1:2], messageBytes)
	copy(resultBytes[2:3], byteOrderingBytes)
	copy(resultBytes[3:4], errorCodeBytes)
	copy(resultBytes[4:5], timeOutBytes)
	copy(resultBytes[5:5+noOfElementSize], noOfElementBytes)
	copy(resultBytes[9:9+size], bytes[:size])

	return resultBytes, 9 + size
}

// Length of Element 4 Byte
func AddElementHeader(length int32, bytes []byte, size int32) ([]byte, int32) {
	resultBytes := make([]byte, 4+size)

	lengtBytes, lengthSize := ToBytes(length)

	copy(resultBytes[0:0+lengthSize], lengtBytes)
	copy(resultBytes[4:4+size], bytes[:size])

	return resultBytes, 4 + size
}

// Data Type 1 Byte
// Length of variable 4 Byte
func AddVariableHeader(dataType, length int32, bytes []byte, size int32) ([]byte, int32) {
	resultBytes := make([]byte, 5+size)

	dataTypeBytes := Int32ToByte(dataType)
	lengtBytes, lengthSize := ToBytes(length)

	copy(resultBytes[0:1], dataTypeBytes)
	copy(resultBytes[1:1+lengthSize], lengtBytes)
	copy(resultBytes[5:5+size], bytes[:size])

	return resultBytes, 5 + size
}

func SetField(dataClass interface{}, index int32, value interface{}, serviceType, messageType int32) interface{} {
	switch {
	case serviceType == int32(QUERY_FLIGHTID) && messageType == int32(REQUEST):
		struc, _ := dataClass.(QueryFlightIdRequest)
		switch index {
		case 0:
			struc.Source = value.(string)
			dataClass = struc
			break
		case 1:
			struc.Destination = value.(string)
			dataClass = struc
			break
		}
	case serviceType == int32(QUERY_FLIGHTID) && messageType == int32(REPLY):
		struc, _ := dataClass.(QueryFlightIdResponse)
		switch index {
		case 0:
			struc.FlightId = value.(int32)
			dataClass = struc
			break
		}
	case serviceType == int32(QUERY_DEPARTURETIME) && messageType == int32(REQUEST):
		struc, _ := dataClass.(QueryDepartureTimeRequest)
		switch index {
		case 0:
			struc.FlightId = value.(int32)
			dataClass = struc
			break
		}
	case serviceType == int32(QUERY_DEPARTURETIME) && messageType == int32(REPLY):
		struc, _ := dataClass.(QueryDepartureTimeResponse)
		switch index {
		case 0:
			struc.DepartureTime = value.(time.Time)
			dataClass = struc
			break
		case 1:
			struc.AirFare = value.(float32)
			dataClass = struc
			break
		case 2:
			struc.SeatAvailability = value.(int32)
			dataClass = struc
			break
		}
	case serviceType == int32(RESERVATION) && messageType == int32(REQUEST):
		struc, _ := dataClass.(ReservationRequest)
		switch index {
		case 0:
			struc.FlightId = value.(int32)
			dataClass = struc
			break
		case 1:
			struc.NoOfSeats = value.(int32)
			dataClass = struc
			break
		}
	case serviceType == int32(RESERVATION) && messageType == int32(REPLY):
		struc, _ := dataClass.(ReservationResponse)
		switch index {
		case 0:
			struc.Msg = value.(string)
			dataClass = struc
			break
		}
	case serviceType == int32(MONITOR) && messageType == int32(REQUEST):
		struc, _ := dataClass.(MonitorRequest)
		switch index {
		case 0:
			struc.FlightId = value.(int32)
			dataClass = struc
			break
		case 1:
			struc.MonitorInterval = value.(int32)
			dataClass = struc
			break
		}
	case serviceType == int32(MONITOR) && messageType == int32(REPLY):
		struc, _ := dataClass.(MonitorResponse)
		switch index {
		case 0:
			struc.Msg = value.(string)
			dataClass = struc
			break
		}
	case serviceType == int32(CHECK_RESERVATION) && messageType == int32(REQUEST):
		struc, _ := dataClass.(CheckReservationRequest)
		switch index {
		case 0:
			struc.FlightId = value.(int32)
			dataClass = struc
			break
		}
	case serviceType == int32(CHECK_RESERVATION) && messageType == int32(REPLY):
		struc, _ := dataClass.(CheckReservationResponse)
		switch index {
		case 0:
			struc.SeatsReserved = value.(int32)
			dataClass = struc
			break
		}
	case serviceType == int32(CANCELLATION) && messageType == int32(REQUEST):
		struc, _ := dataClass.(CancellationRequest)
		switch index {
		case 0:
			struc.FlightId = value.(int32)
			dataClass = struc
			break
		}
	case serviceType == int32(CANCELLATION) && messageType == int32(REPLY):
		struc, _ := dataClass.(CancellationResponse)
		switch index {
		case 0:
			struc.Msg = value.(string)
			dataClass = struc
			break
		}
	}
	return dataClass
}

func decodeIPFromRequestId(requestId []byte) string {
	ip := BytesToString(requestId[0:15])
	re := regexp.MustCompile(`[^.\d]+`)

	return re.ReplaceAllString(ip, "")
}

func DecodeRequestHeader(requestHeader []byte) (int32, int32, int32, int32, int32, int32) {
	byteOrdering := ByteToInt32(requestHeader[2:3])
	serviceType := ByteToInt32(requestHeader[0:1])
	messageType := ByteToInt32(requestHeader[1:2])
	errorCode := ByteToInt32(requestHeader[3:4])
	timeOut := ByteToInt32(requestHeader[4:5])
	noOfElement := BytesToInt32(requestHeader[5:], byteOrdering)

	return byteOrdering, serviceType, messageType, errorCode, timeOut, noOfElement
}

func DecodeElementHeader(elementsByte []byte, byteOrdering int32) (int32, []byte) {
	lengthOfElement := BytesToInt32(elementsByte[:4], byteOrdering)
	variablesByte := elementsByte[4 : 4+lengthOfElement]

	return lengthOfElement, variablesByte
}

func DecodeVariableHeader(variableHeader []byte, byteOrdering int32) (int32, int32) {
	dataType := ByteToInt32(variableHeader[0:1])
	lengthOfVariable := BytesToInt32(variableHeader[1:], byteOrdering)

	return dataType, lengthOfVariable
}

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
			case int32(INT_TYPE):
				query[i] = SetField(
					query[i],
					index,
					BytesToInt32(variableByte, byteOrdering),
					serviceType,
					messageType,
				)
				break
			case int32(FLOAT_TYPE):
				query[i] = SetField(
					query[i],
					index,
					BytesToFloat32(variableByte, byteOrdering),
					serviceType,
					messageType,
				)
				break
			case int32(STRING_TYPE):
				query[i] = SetField(
					query[i],
					index,
					BytesToString(variableByte),
					serviceType,
					messageType,
				)
				break
			case int32(TIME_TYPE):
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

func DecodeError(queryResponse Response, elementsByte []byte, byteOrdering int32) Response {
	lengthOfElement, variablesByte := DecodeElementHeader(elementsByte, byteOrdering)
	elementsByte = elementsByte[4+lengthOfElement:]

	variableHeader := variablesByte[:5]
	_, lengthOfVariable := DecodeVariableHeader(variableHeader, byteOrdering)
	variableByte := variablesByte[5 : 5+lengthOfVariable]

	queryResponse.Error = BytesToString(variableByte)

	return queryResponse
}

// 8 Bytes Request Header
// 4 Bytes Element Header
// 5 Bytes Variable Header
func Unmarshal(bytesStr []byte) (queryRequest []interface{}, queryResponse Response, serviceType, errorCode, timeOut int32) {
	requestHeader := bytesStr[:9]
	byteOrdering, serviceType, messageType, errorCode, timeOut, noOfElement := DecodeRequestHeader(requestHeader)

	elementsByte := bytesStr[9:]

	if errorCode != 0 && messageType == int32(REPLY) {
		queryResponse := Response{}
		queryResponse = DecodeError(queryResponse, elementsByte, byteOrdering)
		return nil, queryResponse, serviceType, errorCode, timeOut
	}

	if messageType == int32(REQUEST) {
		// var queryRequest []interface{}
		switch serviceType {
		case int32(QUERY_FLIGHTID):
			queryRequest = make([]interface{}, noOfElement)
			for i := range queryRequest {
				queryRequest[i] = QueryFlightIdRequest{}
			}
			break
		case int32(QUERY_DEPARTURETIME):
			queryRequest = make([]interface{}, noOfElement)
			for i := range queryRequest {
				queryRequest[i] = QueryDepartureTimeRequest{}
			}
			break
		case int32(RESERVATION):
			queryRequest = make([]interface{}, noOfElement)
			for i := range queryRequest {
				queryRequest[i] = ReservationRequest{}
			}
			break
		case int32(MONITOR):
			queryRequest = make([]interface{}, noOfElement)
			for i := range queryRequest {
				queryRequest[i] = MonitorRequest{}
			}
			break
		case int32(CHECK_RESERVATION):
			queryRequest = make([]interface{}, noOfElement)
			for i := range queryRequest {
				queryRequest[i] = CheckReservationRequest{}
			}
			break
		case int32(CANCELLATION):
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

		return queryRequest, Response{}, serviceType, errorCode, timeOut
	} else if messageType == int32(REPLY) {
		queryResponse := Response{}
		switch serviceType {
		case int32(QUERY_FLIGHTID):
			queryResponse.Value = make([]interface{}, noOfElement)
			for i := range queryResponse.Value {
				queryResponse.Value[i] = QueryFlightIdResponse{}
			}
			break
		case int32(QUERY_DEPARTURETIME):
			queryResponse.Value = make([]interface{}, noOfElement)
			for i := range queryResponse.Value {
				queryResponse.Value[i] = QueryDepartureTimeResponse{}
			}
			break
		case int32(RESERVATION):
			queryResponse.Value = make([]interface{}, noOfElement)
			for i := range queryResponse.Value {
				queryResponse.Value[i] = ReservationResponse{}
			}
			break
		case int32(MONITOR):
			queryResponse.Value = make([]interface{}, noOfElement)
			for i := range queryResponse.Value {
				queryResponse.Value[i] = MonitorResponse{}
			}
			break
		case int32(CHECK_RESERVATION):
			queryResponse.Value = make([]interface{}, noOfElement)
			for i := range queryResponse.Value {
				queryResponse.Value[i] = CheckReservationResponse{}
			}
			break
		case int32(CANCELLATION):
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

		return nil, queryResponse, serviceType, errorCode, timeOut
	}
	return nil, Response{}, serviceType, errorCode, timeOut
}

func Marshal(r interface{}, serviceType, messageType, errorCode, timeOut int32) ([]byte, int32) {
	length := int32(1)
	resultSize := int32(0)
	resultBytes := []byte{}

	if errorCode != 0 && messageType == int32(REPLY) {
		errorBytes, errorSize := ToBytes(r.(*Response).Error)
		errorBytes, errorSize = AddVariableHeader(int32(STRING_TYPE), errorSize, errorBytes, errorSize)
		errorBytes, errorSize = AddElementHeader(errorSize, errorBytes, errorSize)

		resultSize += errorSize
		resultBytes = append(resultBytes, errorBytes...)
		bytes, size := AddRequestHeader(
			serviceType, messageType, errorCode, timeOut, length, resultBytes, resultSize,
		)
		return bytes, size
	}

	if messageType == int32(REQUEST) {
		tempSize := int32(0)
		tempBytes := []byte{}

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
	} else if messageType == int32(REPLY) {
		length = int32(len(r.(*Response).Value))

		for _, dataFields := range r.(*Response).Value {
			tempSize := int32(0)
			tempBytes := []byte{}

			v := reflect.ValueOf(dataFields)

			for i := 0; i < v.NumField(); i++ {
				fieldBytes, fieldSize := ToBytes(v.Field(i).Interface())
				fieldBytes, fieldSize = AddVariableHeader(
					GetDataType(v.Field(i).Interface()), fieldSize, fieldBytes, fieldSize,
				)
				tempBytes = append(tempBytes, fieldBytes...)
				tempSize += fieldSize
			}

			// for _, field := range structs.Fields(dataFields) {
			// 	fieldBytes, fieldSize := ToBytes(field.Value())
			// 	fieldBytes, fieldSize = AddVariableHeader(
			// 		GetDataType(field.Value()), fieldSize, fieldBytes, fieldSize,
			// 	)
			// 	tempBytes = append(tempBytes, fieldBytes...)
			// 	tempSize += fieldSize
			// }
			// tempBytes, tempSize = AddElementHeader(tempSize, tempBytes, tempSize)

			resultSize += tempSize
			resultBytes = append(resultBytes, tempBytes...)
		}
	}

	bytes, size := AddRequestHeader(
		serviceType, messageType, errorCode, timeOut, length, resultBytes, resultSize,
	)
	return bytes, size
}
