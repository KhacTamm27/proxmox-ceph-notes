# Một node chết hẳn (hỏng phần cứng): khôi phục dịch vụ

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Một node mất hoàn toàn (không bật lại được), VM trên node đó ngừng, GUI hiện node đỏ, Ceph báo OSD down và PG degraded.

**Nguyên nhân hay gặp:** Hỏng phần cứng, nguồn, mainboard. Cluster còn quorum nhưng cần đưa dịch vụ lên node khác.

## Các bước xử lý

1. Xác nhận node thật sự chết (không chỉ đứt mạng) và cluster còn quorum

```bash
pvecm status
```

2. Tình trạng Ceph: cluster sẽ degraded nhưng vẫn phục vụ nếu còn đủ bản sao

```bash
ceph -s
ceph osd tree down
```

3. VM có HA sẽ tự chạy lại sau khi fence, xem trạng thái

```bash
ha-manager status
```

4. VM không HA mà đĩa nằm trên Ceph: chuyển file cấu hình sang node còn sống rồi start (CHỈ khi chắc node chết đã tắt hẳn)

```bash
mv /etc/pve/nodes/<dead-node>/qemu-server/<vmid>.conf /etc/pve/nodes/<alive-node>/qemu-server/
qm start <vmid>
```

5. Nếu thay thế node sẽ lâu, để Ceph tự recover; nếu sắp đưa lại trong thời gian ngắn, đặt noout để tránh rebalance

```bash
ceph osd set noout
```

## Lưu ý

Không bao giờ chạy cùng một VM ở hai node: hai bản cùng ghi vào một đĩa sẽ hỏng dữ liệu. Tắt hẳn node chết (rút nguồn, IPMI power off) trước khi chuyển cấu hình. Sau khi node mới vào lại, theo case xóa node hỏng và join lại cùng tên.

<!-- từ khóa: proxmox node chết hỏng phần cứng khôi phục vm không ha move config qemu-server ceph degraded mất node -->
