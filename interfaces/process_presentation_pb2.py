# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: interfaces/process_presentation.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'interfaces/process_presentation.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n%interfaces/process_presentation.proto\x12\x0cpresentation\"?\n\x1aProcessPresentationRequest\x12\x10\n\x08\x66ilepath\x18\x01 \x01(\t\x12\x0f\n\x07user_id\x18\x02 \x01(\t\".\n\x1bProcessPresentationResponse\x12\x0f\n\x07task_id\x18\x01 \x01(\t\"$\n\x11TaskStatusRequest\x12\x0f\n\x07task_id\x18\x01 \x01(\t\"4\n\x12TaskStatusResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0e\n\x06result\x18\x02 \x01(\t2\xdc\x01\n\x1aProcessPresentationService\x12j\n\x13ProcessPresentation\x12(.presentation.ProcessPresentationRequest\x1a).presentation.ProcessPresentationResponse\x12R\n\rGetTaskStatus\x12\x1f.presentation.TaskStatusRequest\x1a .presentation.TaskStatusResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'interfaces.process_presentation_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_PROCESSPRESENTATIONREQUEST']._serialized_start=55
  _globals['_PROCESSPRESENTATIONREQUEST']._serialized_end=118
  _globals['_PROCESSPRESENTATIONRESPONSE']._serialized_start=120
  _globals['_PROCESSPRESENTATIONRESPONSE']._serialized_end=166
  _globals['_TASKSTATUSREQUEST']._serialized_start=168
  _globals['_TASKSTATUSREQUEST']._serialized_end=204
  _globals['_TASKSTATUSRESPONSE']._serialized_start=206
  _globals['_TASKSTATUSRESPONSE']._serialized_end=258
  _globals['_PROCESSPRESENTATIONSERVICE']._serialized_start=261
  _globals['_PROCESSPRESENTATIONSERVICE']._serialized_end=481
# @@protoc_insertion_point(module_scope)
