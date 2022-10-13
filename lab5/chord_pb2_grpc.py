# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chord.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='chord.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x0b\x63hord.proto\"\"\n\x0fRegisterRequest\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\"L\n\rRegisterReply\x12\n\n\x02id\x18\x01 \x01(\r\x12\x17\n\rerror_message\x18\x02 \x01(\tH\x00\x12\x0b\n\x01m\x18\x03 \x01(\rH\x00\x42\t\n\x07message\"$\n\x11\x44\x65registerRequest\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\r\"2\n\x0f\x44\x65registerReply\x12\x0e\n\x06result\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"\"\n\x0fPopulateRequest\x12\x0f\n\x07node_id\x18\x01 \x01(\r\"`\n\rPopulateReply\x12&\n\x0bpredecessor\x18\x01 \x01(\x0b\x32\x11.FingerTableEntry\x12\'\n\x0c\x66inger_table\x18\x02 \x03(\x0b\x32\x11.FingerTableEntry\"4\n\x10\x46ingerTableEntry\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\"\r\n\x0bInfoRequest\"_\n\tInfoReply\x12$\n\x05nodes\x18\x01 \x03(\x0b\x32\x15.InfoReply.NodesEntry\x1a,\n\nNodesEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"(\n\x0bSaveRequest\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\"R\n\tSaveReply\x12\x0e\n\x06result\x18\x01 \x01(\x08\x12\x11\n\x07node_id\x18\x02 \x01(\rH\x00\x12\x17\n\rerror_message\x18\x03 \x01(\tH\x00\x42\t\n\x07message\"\x1c\n\rRemoveRequest\x12\x0b\n\x03key\x18\x01 \x01(\t\"T\n\x0bRemoveReply\x12\x0e\n\x06result\x18\x01 \x01(\x08\x12\x11\n\x07node_id\x18\x02 \x01(\rH\x00\x12\x17\n\rerror_message\x18\x03 \x01(\tH\x00\x42\t\n\x07message\"\x1a\n\x0b\x46indRequest\x12\x0b\n\x03key\x18\x01 \x01(\t\"b\n\tFindReply\x12\x0e\n\x06result\x18\x01 \x01(\x08\x12!\n\x04node\x18\x02 \x01(\x0b\x32\x11.FingerTableEntryH\x00\x12\x17\n\rerror_message\x18\x03 \x01(\tH\x00\x42\t\n\x07message\"\r\n\x0bQuitRequest\"\x1c\n\tQuitReply\x12\x0f\n\x07message\x18\x01 \x01(\t2\xd3\x01\n\x08Registry\x12,\n\x08register\x12\x10.RegisterRequest\x1a\x0e.RegisterReply\x12\x32\n\nderegister\x12\x12.DeregisterRequest\x1a\x10.DeregisterReply\x12\x39\n\x15populate_finger_table\x12\x10.PopulateRequest\x1a\x0e.PopulateReply\x12*\n\x0eget_chord_info\x12\x0c.InfoRequest\x1a\n.InfoReply2\xce\x01\n\x04Node\x12,\n\x10get_finger_table\x12\x0c.InfoRequest\x1a\n.InfoReply\x12$\n\x08save_key\x12\x0c.SaveRequest\x1a\n.SaveReply\x12*\n\nremove_key\x12\x0e.RemoveRequest\x1a\x0c.RemoveReply\x12$\n\x08\x66ind_key\x12\x0c.FindRequest\x1a\n.FindReply\x12 \n\x04quit\x12\x0c.QuitRequest\x1a\n.QuitReplyb\x06proto3')
)




_REGISTERREQUEST = _descriptor.Descriptor(
  name='RegisterRequest',
  full_name='RegisterRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='address', full_name='RegisterRequest.address', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=15,
  serialized_end=49,
)


_REGISTERREPLY = _descriptor.Descriptor(
  name='RegisterReply',
  full_name='RegisterReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='RegisterReply.id', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='error_message', full_name='RegisterReply.error_message', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='m', full_name='RegisterReply.m', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='message', full_name='RegisterReply.message',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=51,
  serialized_end=127,
)


_DEREGISTERREQUEST = _descriptor.Descriptor(
  name='DeregisterRequest',
  full_name='DeregisterRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='address', full_name='DeregisterRequest.address', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=129,
  serialized_end=165,
)


_DEREGISTERREPLY = _descriptor.Descriptor(
  name='DeregisterReply',
  full_name='DeregisterReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='result', full_name='DeregisterReply.result', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='message', full_name='DeregisterReply.message', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=167,
  serialized_end=217,
)


_POPULATEREQUEST = _descriptor.Descriptor(
  name='PopulateRequest',
  full_name='PopulateRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='node_id', full_name='PopulateRequest.node_id', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=219,
  serialized_end=253,
)


_POPULATEREPLY = _descriptor.Descriptor(
  name='PopulateReply',
  full_name='PopulateReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='predecessor', full_name='PopulateReply.predecessor', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='finger_table', full_name='PopulateReply.finger_table', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=255,
  serialized_end=351,
)


_FINGERTABLEENTRY = _descriptor.Descriptor(
  name='FingerTableEntry',
  full_name='FingerTableEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='node_id', full_name='FingerTableEntry.node_id', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='address', full_name='FingerTableEntry.address', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=353,
  serialized_end=405,
)


_INFOREQUEST = _descriptor.Descriptor(
  name='InfoRequest',
  full_name='InfoRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=407,
  serialized_end=420,
)


_INFOREPLY_NODESENTRY = _descriptor.Descriptor(
  name='NodesEntry',
  full_name='InfoReply.NodesEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='InfoReply.NodesEntry.key', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='InfoReply.NodesEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=473,
  serialized_end=517,
)

_INFOREPLY = _descriptor.Descriptor(
  name='InfoReply',
  full_name='InfoReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='nodes', full_name='InfoReply.nodes', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_INFOREPLY_NODESENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=422,
  serialized_end=517,
)


_SAVEREQUEST = _descriptor.Descriptor(
  name='SaveRequest',
  full_name='SaveRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='SaveRequest.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='text', full_name='SaveRequest.text', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=519,
  serialized_end=559,
)


_SAVEREPLY = _descriptor.Descriptor(
  name='SaveReply',
  full_name='SaveReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='result', full_name='SaveReply.result', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='node_id', full_name='SaveReply.node_id', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='error_message', full_name='SaveReply.error_message', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='message', full_name='SaveReply.message',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=561,
  serialized_end=643,
)


_REMOVEREQUEST = _descriptor.Descriptor(
  name='RemoveRequest',
  full_name='RemoveRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='RemoveRequest.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=645,
  serialized_end=673,
)


_REMOVEREPLY = _descriptor.Descriptor(
  name='RemoveReply',
  full_name='RemoveReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='result', full_name='RemoveReply.result', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='node_id', full_name='RemoveReply.node_id', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='error_message', full_name='RemoveReply.error_message', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='message', full_name='RemoveReply.message',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=675,
  serialized_end=759,
)


_FINDREQUEST = _descriptor.Descriptor(
  name='FindRequest',
  full_name='FindRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='FindRequest.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=761,
  serialized_end=787,
)


_FINDREPLY = _descriptor.Descriptor(
  name='FindReply',
  full_name='FindReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='result', full_name='FindReply.result', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='node', full_name='FindReply.node', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='error_message', full_name='FindReply.error_message', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='message', full_name='FindReply.message',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=789,
  serialized_end=887,
)


_QUITREQUEST = _descriptor.Descriptor(
  name='QuitRequest',
  full_name='QuitRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=889,
  serialized_end=902,
)


_QUITREPLY = _descriptor.Descriptor(
  name='QuitReply',
  full_name='QuitReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='QuitReply.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=904,
  serialized_end=932,
)

_REGISTERREPLY.oneofs_by_name['message'].fields.append(
  _REGISTERREPLY.fields_by_name['error_message'])
_REGISTERREPLY.fields_by_name['error_message'].containing_oneof = _REGISTERREPLY.oneofs_by_name['message']
_REGISTERREPLY.oneofs_by_name['message'].fields.append(
  _REGISTERREPLY.fields_by_name['m'])
_REGISTERREPLY.fields_by_name['m'].containing_oneof = _REGISTERREPLY.oneofs_by_name['message']
_POPULATEREPLY.fields_by_name['predecessor'].message_type = _FINGERTABLEENTRY
_POPULATEREPLY.fields_by_name['finger_table'].message_type = _FINGERTABLEENTRY
_INFOREPLY_NODESENTRY.containing_type = _INFOREPLY
_INFOREPLY.fields_by_name['nodes'].message_type = _INFOREPLY_NODESENTRY
_SAVEREPLY.oneofs_by_name['message'].fields.append(
  _SAVEREPLY.fields_by_name['node_id'])
_SAVEREPLY.fields_by_name['node_id'].containing_oneof = _SAVEREPLY.oneofs_by_name['message']
_SAVEREPLY.oneofs_by_name['message'].fields.append(
  _SAVEREPLY.fields_by_name['error_message'])
_SAVEREPLY.fields_by_name['error_message'].containing_oneof = _SAVEREPLY.oneofs_by_name['message']
_REMOVEREPLY.oneofs_by_name['message'].fields.append(
  _REMOVEREPLY.fields_by_name['node_id'])
_REMOVEREPLY.fields_by_name['node_id'].containing_oneof = _REMOVEREPLY.oneofs_by_name['message']
_REMOVEREPLY.oneofs_by_name['message'].fields.append(
  _REMOVEREPLY.fields_by_name['error_message'])
_REMOVEREPLY.fields_by_name['error_message'].containing_oneof = _REMOVEREPLY.oneofs_by_name['message']
_FINDREPLY.fields_by_name['node'].message_type = _FINGERTABLEENTRY
_FINDREPLY.oneofs_by_name['message'].fields.append(
  _FINDREPLY.fields_by_name['node'])
_FINDREPLY.fields_by_name['node'].containing_oneof = _FINDREPLY.oneofs_by_name['message']
_FINDREPLY.oneofs_by_name['message'].fields.append(
  _FINDREPLY.fields_by_name['error_message'])
_FINDREPLY.fields_by_name['error_message'].containing_oneof = _FINDREPLY.oneofs_by_name['message']
DESCRIPTOR.message_types_by_name['RegisterRequest'] = _REGISTERREQUEST
DESCRIPTOR.message_types_by_name['RegisterReply'] = _REGISTERREPLY
DESCRIPTOR.message_types_by_name['DeregisterRequest'] = _DEREGISTERREQUEST
DESCRIPTOR.message_types_by_name['DeregisterReply'] = _DEREGISTERREPLY
DESCRIPTOR.message_types_by_name['PopulateRequest'] = _POPULATEREQUEST
DESCRIPTOR.message_types_by_name['PopulateReply'] = _POPULATEREPLY
DESCRIPTOR.message_types_by_name['FingerTableEntry'] = _FINGERTABLEENTRY
DESCRIPTOR.message_types_by_name['InfoRequest'] = _INFOREQUEST
DESCRIPTOR.message_types_by_name['InfoReply'] = _INFOREPLY
DESCRIPTOR.message_types_by_name['SaveRequest'] = _SAVEREQUEST
DESCRIPTOR.message_types_by_name['SaveReply'] = _SAVEREPLY
DESCRIPTOR.message_types_by_name['RemoveRequest'] = _REMOVEREQUEST
DESCRIPTOR.message_types_by_name['RemoveReply'] = _REMOVEREPLY
DESCRIPTOR.message_types_by_name['FindRequest'] = _FINDREQUEST
DESCRIPTOR.message_types_by_name['FindReply'] = _FINDREPLY
DESCRIPTOR.message_types_by_name['QuitRequest'] = _QUITREQUEST
DESCRIPTOR.message_types_by_name['QuitReply'] = _QUITREPLY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

RegisterRequest = _reflection.GeneratedProtocolMessageType('RegisterRequest', (_message.Message,), dict(
  DESCRIPTOR = _REGISTERREQUEST,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:RegisterRequest)
  ))
_sym_db.RegisterMessage(RegisterRequest)

RegisterReply = _reflection.GeneratedProtocolMessageType('RegisterReply', (_message.Message,), dict(
  DESCRIPTOR = _REGISTERREPLY,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:RegisterReply)
  ))
_sym_db.RegisterMessage(RegisterReply)

DeregisterRequest = _reflection.GeneratedProtocolMessageType('DeregisterRequest', (_message.Message,), dict(
  DESCRIPTOR = _DEREGISTERREQUEST,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:DeregisterRequest)
  ))
_sym_db.RegisterMessage(DeregisterRequest)

DeregisterReply = _reflection.GeneratedProtocolMessageType('DeregisterReply', (_message.Message,), dict(
  DESCRIPTOR = _DEREGISTERREPLY,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:DeregisterReply)
  ))
_sym_db.RegisterMessage(DeregisterReply)

PopulateRequest = _reflection.GeneratedProtocolMessageType('PopulateRequest', (_message.Message,), dict(
  DESCRIPTOR = _POPULATEREQUEST,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:PopulateRequest)
  ))
_sym_db.RegisterMessage(PopulateRequest)

PopulateReply = _reflection.GeneratedProtocolMessageType('PopulateReply', (_message.Message,), dict(
  DESCRIPTOR = _POPULATEREPLY,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:PopulateReply)
  ))
_sym_db.RegisterMessage(PopulateReply)

FingerTableEntry = _reflection.GeneratedProtocolMessageType('FingerTableEntry', (_message.Message,), dict(
  DESCRIPTOR = _FINGERTABLEENTRY,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:FingerTableEntry)
  ))
_sym_db.RegisterMessage(FingerTableEntry)

InfoRequest = _reflection.GeneratedProtocolMessageType('InfoRequest', (_message.Message,), dict(
  DESCRIPTOR = _INFOREQUEST,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:InfoRequest)
  ))
_sym_db.RegisterMessage(InfoRequest)

InfoReply = _reflection.GeneratedProtocolMessageType('InfoReply', (_message.Message,), dict(

  NodesEntry = _reflection.GeneratedProtocolMessageType('NodesEntry', (_message.Message,), dict(
    DESCRIPTOR = _INFOREPLY_NODESENTRY,
    __module__ = 'chord_pb2'
    # @@protoc_insertion_point(class_scope:InfoReply.NodesEntry)
    ))
  ,
  DESCRIPTOR = _INFOREPLY,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:InfoReply)
  ))
_sym_db.RegisterMessage(InfoReply)
_sym_db.RegisterMessage(InfoReply.NodesEntry)

SaveRequest = _reflection.GeneratedProtocolMessageType('SaveRequest', (_message.Message,), dict(
  DESCRIPTOR = _SAVEREQUEST,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:SaveRequest)
  ))
_sym_db.RegisterMessage(SaveRequest)

SaveReply = _reflection.GeneratedProtocolMessageType('SaveReply', (_message.Message,), dict(
  DESCRIPTOR = _SAVEREPLY,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:SaveReply)
  ))
_sym_db.RegisterMessage(SaveReply)

RemoveRequest = _reflection.GeneratedProtocolMessageType('RemoveRequest', (_message.Message,), dict(
  DESCRIPTOR = _REMOVEREQUEST,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:RemoveRequest)
  ))
_sym_db.RegisterMessage(RemoveRequest)

RemoveReply = _reflection.GeneratedProtocolMessageType('RemoveReply', (_message.Message,), dict(
  DESCRIPTOR = _REMOVEREPLY,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:RemoveReply)
  ))
_sym_db.RegisterMessage(RemoveReply)

FindRequest = _reflection.GeneratedProtocolMessageType('FindRequest', (_message.Message,), dict(
  DESCRIPTOR = _FINDREQUEST,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:FindRequest)
  ))
_sym_db.RegisterMessage(FindRequest)

FindReply = _reflection.GeneratedProtocolMessageType('FindReply', (_message.Message,), dict(
  DESCRIPTOR = _FINDREPLY,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:FindReply)
  ))
_sym_db.RegisterMessage(FindReply)

QuitRequest = _reflection.GeneratedProtocolMessageType('QuitRequest', (_message.Message,), dict(
  DESCRIPTOR = _QUITREQUEST,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:QuitRequest)
  ))
_sym_db.RegisterMessage(QuitRequest)

QuitReply = _reflection.GeneratedProtocolMessageType('QuitReply', (_message.Message,), dict(
  DESCRIPTOR = _QUITREPLY,
  __module__ = 'chord_pb2'
  # @@protoc_insertion_point(class_scope:QuitReply)
  ))
_sym_db.RegisterMessage(QuitReply)


_INFOREPLY_NODESENTRY._options = None

_REGISTRY = _descriptor.ServiceDescriptor(
  name='Registry',
  full_name='Registry',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=935,
  serialized_end=1146,
  methods=[
  _descriptor.MethodDescriptor(
    name='register',
    full_name='Registry.register',
    index=0,
    containing_service=None,
    input_type=_REGISTERREQUEST,
    output_type=_REGISTERREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='deregister',
    full_name='Registry.deregister',
    index=1,
    containing_service=None,
    input_type=_DEREGISTERREQUEST,
    output_type=_DEREGISTERREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='populate_finger_table',
    full_name='Registry.populate_finger_table',
    index=2,
    containing_service=None,
    input_type=_POPULATEREQUEST,
    output_type=_POPULATEREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='get_chord_info',
    full_name='Registry.get_chord_info',
    index=3,
    containing_service=None,
    input_type=_INFOREQUEST,
    output_type=_INFOREPLY,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_REGISTRY)

DESCRIPTOR.services_by_name['Registry'] = _REGISTRY


_NODE = _descriptor.ServiceDescriptor(
  name='Node',
  full_name='Node',
  file=DESCRIPTOR,
  index=1,
  serialized_options=None,
  serialized_start=1149,
  serialized_end=1355,
  methods=[
  _descriptor.MethodDescriptor(
    name='get_finger_table',
    full_name='Node.get_finger_table',
    index=0,
    containing_service=None,
    input_type=_INFOREQUEST,
    output_type=_INFOREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='save_key',
    full_name='Node.save_key',
    index=1,
    containing_service=None,
    input_type=_SAVEREQUEST,
    output_type=_SAVEREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='remove_key',
    full_name='Node.remove_key',
    index=2,
    containing_service=None,
    input_type=_REMOVEREQUEST,
    output_type=_REMOVEREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='find_key',
    full_name='Node.find_key',
    index=3,
    containing_service=None,
    input_type=_FINDREQUEST,
    output_type=_FINDREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='quit',
    full_name='Node.quit',
    index=4,
    containing_service=None,
    input_type=_QUITREQUEST,
    output_type=_QUITREPLY,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_NODE)

DESCRIPTOR.services_by_name['Node'] = _NODE

# @@protoc_insertion_point(module_scope)