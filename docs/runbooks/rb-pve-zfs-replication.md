# Proxmox ZFS replication: cấu hình và kiểm thử khôi phục VM

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Cấu hình replication ZFS định kỳ giữa các node trong cùng cluster PVE và kiểm thử khả năng khôi phục mà không tạo VM trùng hoặc gây split-brain.

**Điều kiện trước khi làm:** Các node đã join cùng cluster và có quorum. Mỗi node có ZFS pool khỏe; storage ID phải được khai báo nhất quán, storage đích khả dụng và đủ dung lượng. Có backup riêng: replication không thay thế backup và không sao chép trạng thái RAM của VM.

## Các bước

1. Kiểm tra cluster, ZFS pool và storage trên node nguồn/đích

```bash
pvecm status
zpool status -v
pvesm status
```

2. Trên Datacenter > Replication > Add, chọn VM nguồn, node đích và schedule; bảo đảm mọi disk cần bảo vệ nằm trên storage hỗ trợ replication

3. Chạy đồng bộ đầu tiên, kiểm tra job status/log và xác nhận volume đã có trên storage node đích

```bash
pvesr status
zpool status -v
```

4. Diễn tập khôi phục trong cửa sổ bảo trì: xác nhận VM nguồn đã tắt/fenced trước, rồi start VM ở node đích theo quy trình vận hành; kiểm tra OS, ứng dụng, network và độ mới dữ liệu

```bash
pvesr status
qm status <vmid>
```

## Lưu ý

Không tạo VM thứ hai với VMID khác rồi đổi VMID thủ công sau replication. Proxmox quản lý cấu hình và volume replica theo job; sửa tay hoặc khởi chạy đồng thời hai bản VM có thể làm hỏng dữ liệu. Schedule 5 phút chỉ đặt giới hạn mục tiêu RPO theo lịch, không bảo đảm bản sao luôn mới đúng 5 phút; lần chạy lỗi hoặc kéo dài sẽ làm RPO tăng. Replication đơn thuần không tự bật VM khi node lỗi trừ khi đã cấu hình HA theo cách phù hợp. Không start bản replica khi chưa chắc node nguồn đã tắt/fenced.

## Nguồn tham khảo

- [Proxmox VE pvesr manual](https://pve.proxmox.com/pve-docs/pvesr.1.html)

<!-- từ khóa: proxmox pve zfs replication replicate pvesr sao chép VM node đích target schedule RPO failover recovery -->
