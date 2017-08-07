# Copyright (C) 2009 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Emit commands needed for Rockchip devices during OTA installation
(installing the RK30xxLoader.bin)."""

import common
import re


def FullOTA_Assertions(info):
  ## we suggest not update the parameter.
  #Install_Parameter(info)
  AddBootloaderAssertion(info, info.input_zip)

def IncrementalOTA_Assertions(info):
  AddBootloaderAssertion(info, info.target_zip)

def AddBootloaderAssertion(info, input_zip):
  android_info = input_zip.read("OTA/android-info.txt")
  m = re.search(r"require\s+version-bootloader\s*=\s*(\S+)", android_info)
  if m:
    bootloaders = m.group(1).split("|")
    if "*" not in bootloaders:
      info.script.AssertSomeBootloader(*bootloaders)
    info.metadata["pre-bootloader"] = m.group(1)

def Install_Parameter(info):
  try:
    parameter_bin = info.input_zip.read("PARAMETER/parameter");
  except KeyError:
    print "warning: no parameter in input target_files; not flashing parameter"
    return

  print "find parameter, should add to package"
  common.ZipWriteStr(info.output_zip, "parameter", parameter_bin)
  info.script.Print("start update parameter...")
  info.script.WriteRawParameterImage("/parameter", "parameter")
  info.script.Print("end update parameter")

def InstallRKLoader(loader_bin, input_zip, info):
  try:
    print "wirte RKLoader.bin now..."
    info.script.Print("Writing rk loader bin...")
    common.ZipWriteStr(info.output_zip, "RKLoader.bin", loader_bin)
    info.script.WriteRawLoaderImage()
  except KeyError:
    print "no RKLoader.bin, ignore it."


def InstallVendor1(loader_bin, input_zip, info):
  common.ZipWriteStr(info.output_zip, "vendor1.img", loader_bin)
  info.script.Print("Writing vendor1 img...")
  info.script.WriteRawSparseImage("vendor1", "vendor1.img")

def InstallVendor0(loader_bin, input_zip, info):
  common.ZipWriteStr(info.output_zip, "vendor0.img", loader_bin)
  info.script.Print("Writing vendor0 img...")
  info.script.WriteRawSparseImage("vendor0", "vendor0.img")

def InstallUboot(loader_bin, input_zip, info):
  common.ZipWriteStr(info.output_zip, "uboot.img", loader_bin)
  info.script.Print("Writing uboot loader img...")
  info.script.WriteRawImage("/uboot", "uboot.img")

def InstallTrust(trust_bin, input_zip, info):
  common.ZipWriteStr(info.output_zip, "trust.img", trust_bin)
  info.script.Print("Writing trust img...")
  info.script.WriteRawImage("/trust", "trust.img")

def InstallCharge(charge_bin, input_zip, info):
  common.ZipWriteStr(info.output_zip, "charge.img", charge_bin)
  info.script.Print("Writing charge img..")
  info.script.WriteRawImage("/charge", "charge.img")

def InstallResource(resource_bin, input_zip, info):
  common.ZipWriteStr(info.output_zip, "resource.img", resource_bin)
  info.script.Print("Writing resource image..")
  info.script.WriteRawImage("/resource", "resource.img")

def FullOTA_InstallEnd(info):
  try:
    trust = info.input_zip.read("trust.img")
    print "write trust now..."
    InstallTrust(trust, info.input_zip, info)
  except KeyError:
    print "warning: no trust.img in input target_files; not flashing trust"

  try:
    uboot = info.input_zip.read("uboot.img")
    print "write uboot now..."
    InstallUboot(uboot, info.input_zip, info)
  except KeyError:
    print "warning: no uboot.img in input target_files; not flashing uboot"

  try:
    vendor1 = info.input_zip.read("vendor1.img")
    print "Write vendor1.img"
    InstallVendor1(vendor1, info.input_zip, info)
  except KeyError:
    print "warning: no vendor1.img in input target_files; not flashing vendor1"

  try:
    vendor0 = info.input_zip.read("vendor0.img")
    print "Write vendor0.img"
    InstallVendor0(vendor0, info.input_zip, info)
  except KeyError:
    print "warning: no vendor0.img in input target_files; not flashing vendor0"

  try:
    charge = info.input_zip.read("charge.img")
    print "wirte charge now..."
    InstallCharge(charge, info.input_zip, info)
  except KeyError:
    # print "info: no charge img; ignore it."
    print "no charge img; ignore it."

#**************************************************************************************************
#resource package in the boot.img and recovery.img,so we suggest not to update alone resource.img
#**************************************************************************************************
#
#  try:
#    resource = info.input_zip.read("resource.img")
#    print "wirte resource now..."
#    InstallResource(resource, info.input_zip, info)
#  except KeyError:
#    print "info: no resource image; ignore it."

#  try:
#    loader_bin = info.input_zip.read("LOADER/RKLoader.img")
#  except KeyError:
#    # print "warning: no rk loader bin in input target_files; not flashing loader"
#    print "no rk loader bin in input target_files; not flashing loader"
#    print "to add clear misc command"
#    info.script.ClearMiscCommand()
#    return

  try:
    loader_bin = info.input_zip.read("RKLoader.bin")
    InstallRKLoader(loader_bin, info.input_zip, info)
  except KeyError:
    print "no RKLoader.bin, ignore it."

def IncrementalOTA_InstallEnd(info):
  try:
    vendor0_target = info.target_zip.read("vendor0.img")
  except KeyError:
    vendor0_target = None

  try:
    vendor0_source = info.source_zip.read("vendor0.img")
  except KeyError:
    vendor0_source = None

  if (vendor0_target != None) and (vendor0_target != vendor0_source):
    print "write vendor0 now..."
    InstallVendor0(vendor0_target, info.target_zip, info)
  else:
    print "vendor0 unchanged; skipping"

  try:
    vendor1_target = info.target_zip.read("vendor1.img")
  except KeyError:
    vendor1_target = None

  try:
    vendor1_source = info.source_zip.read("vendor1.img")
  except KeyError:
    vendor1_source = None

  if (vendor1_target != None) and (vendor1_target != vendor1_source):
    print "write vendor1 now..."
    InstallVendor1(vendor1_target, info.target_zip, info)
  else:
    print "vendor1 unchanged; skipping"

  try:
    trust_target = info.target_zip.read("trust.img")
  except KeyError:
    trust_target = None

  try:
    trust_source = info.source_zip.read("trust.img")
  except KeyError:
    trust_source = None

  if (trust_target != None) and (trust_target != trust_source):
    print "write trust now..."
    InstallTrust(trust_target, info.target_zip, info)
  else:
    print "trust unchanged; skipping"

  try:
    loader_uboot_target = info.target_zip.read("uboot.img")
  except KeyError:
    loader_uboot_target = None

  try:
    loader_uboot_source = info.source_zip.read("uboot.img")
  except KeyError:
    loader_uboot_source = None

  if (loader_uboot_target != None) and (loader_uboot_target != loader_uboot_source):
    print "write uboot now..."
    InstallUboot(loader_uboot_target, info.target_zip, info)
  else:
    print "uboot unchanged; skipping"

  try:
    charge_target = info.target_zip.read("charge.img")
  except KeyError:
    charge_target = None

  try:
    charge_source = info.source_zip.read("charge.img")
  except KeyError:
    charge_source = None

  if (charge_target != None) and (charge_target != charge_source):
    print "write charge now..."
    InstallCharge(charge_target, info.target_zip, info)
  else:
    print "charge unchanged; skipping"

#**************************************************************************************************
#resource package in the boot.img and recovery.img,so we suggest not to update alone resource.img
#**************************************************************************************************
#  try:
#    resource_target = info.target_zip.read("resource.img")
#  except KeyError:
#    resource_target = None

#  try:
#    resource_source = info.source_zip.read("resource.img")
#  except KeyError:
#    resource_source = None

#  if (resource_target != None) and (resource_target != resource_source):
#    print "write resource now..."
#    InstallResource(resource_target, info.target_zip, info)
#  else:
#    print "resource unchanged; skipping"

  try:
    target_loader = info.target_zip.read("RKLoader.bin")
  except KeyError:
    print "warning: rk loader bin missing from target; not flashing loader"
    print "clear misc command"
    info.script.ClearMiscCommand()
    return

  try:
    source_loader = info.source_zip.read("RKLoader.bin")
  except KeyError:
    source_loader = None

  if source_loader == target_loader:
    print "RK loader bin unchanged; skipping"
    print "clear misc command"
    info.script.ClearMiscCommand()
    return

  InstallRKLoader(target_loader, info.target_zip, info)
