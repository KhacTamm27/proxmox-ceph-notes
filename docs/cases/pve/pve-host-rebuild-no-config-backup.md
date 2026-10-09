# PVE host hỏng đĩa boot, không có backup cấu hình: kiểm kê và dựng lại node

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Node Proxmox không khởi động do hỏng ổ boot, không có bản backup cấu hình node; VM hoặc dịch vụ Ceph trên node cần được khôi phục.

**Nguyên nhân hay gặp:** Cài lại hệ điều hành làm mất cấu hình cục bộ của node. Trạng thái VM và dữ liệu Ceph có thể vẫn còn trên storage hoặc các ổ dữ liệu, nhưng phải kiểm kê trước khi gỡ node hay khởi tạo lại ổ.

## Các bước xử lý

1. Xác nhận node hỏng thực sự đã tắt, cluster còn quorum và ghi lại trạng thái Ceph/storage

```bash
pvecm status
pvecm nodes
ceph -s
ceph osd tree
pvesm status
```

2. Kiểm kê VM/CT, vị trí disk và dịch vụ từng chạy trên node; không chuyển hoặc sửa file cấu hình hàng loạt

```bash
pvesh get /cluster/resources --type vm
ha-manager status
ceph mon dump
ceph mgr dump
ceph fs status
```

3. Trước khi cài lại: xác định chính xác ổ boot và các ổ dữ liệu cần giữ; ghi lại hostname, IP/VLAN, bridge/OVS, PVE/Ceph version và WWN/serial

```bash
lsblk -o NAME,SIZE,SERIAL,WWN,FSTYPE,MOUNTPOINTS
pveversion -v
```

4. Nếu cần xóa node khỏi cluster hoặc dựng node thay thế, làm theo runbook xóa node và xử lý Ceph trước; chỉ cài lại đúng phiên bản tương thích, cấu hình network rồi mới join

5. Sau khi join, đối chiếu lại membership, Ceph, storage, VM/CT và chứng chỉ trước khi đưa workload trở lại

```bash
pvecm status
ceph -s
ceph osd tree
pvesm status
pvesh get /cluster/resources --type vm
```

## Lưu ý

Không chạy `pvecm delnode`, xóa `/etc/pve/nodes`, format/zap ổ dữ liệu hoặc copy bằng `mv` các file `*.conf` trước khi biết rõ node nào đang sở hữu VM, trạng thái Ceph và loại storage. Không coi lệnh `pvecm delnode` là thao tác dọn OSD/MON/MGR/MDS. Khi thiếu bản backup cấu hình, dựng lại thông tin network và version từ các node còn sống, switch/IPAM và hồ sơ vận hành; không đưa keyring, chứng chỉ riêng, endpoint hoặc credential vào kho tài liệu. Nếu dữ liệu Ceph trên ổ cũ cần giữ, dừng và dùng quy trình recovery Ceph phù hợp thay vì tạo OSD mới lên ổ đó. Xem thêm [runbook xóa node PVE](../../runbooks/rb-pve-remove-node.md).

<!-- từ khóa: proxmox pve host node hỏng disk boot cài lại reinstall không có backup config mất cấu hình network ceph osd mon mgr mds rebuild cluster -->
