# Node dừng: HA khởi động lại đồng loạt VM làm tràn RAM (domino)

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Một node dừng hoặc bị fence, VM của nó tự bật lại trên các host còn lại, RAM các host đầy, hệ thống chậm hoặc sập lan sang node khác.

**Nguyên nhân hay gặp:** Cơ chế fencing đánh dấu node dead rồi migrate hoặc khởi động lại VM trên host khác. VM đang dừng không dùng tài nguyên, nhưng khi nhiều VM bật đồng loạt thì RAM bị chiếm ngay, các host còn lại không đủ chỗ.

## Các bước xử lý

1. Xem HA đang làm gì và VM nào đang bật lại

```bash
ha-manager status
ha-manager config
```

2. Kiểm tra RAM trên các host còn lại

```bash
free -h
pvesh get /nodes/<node>/status
```

3. Trước bảo trì có kế hoạch: tắt HA theo thứ tự (pve-ha-lrm ở mọi host trước, rồi pve-ha-crm), xem runbook bảo trì production

```bash
systemctl stop pve-ha-lrm
systemctl stop pve-ha-crm
```

## Lưu ý

Phòng ngừa tốt nhất là tính dự phòng RAM kiểu N+1 (các node còn lại gánh được VM của node lớn nhất) và không bảo trì khi HA đang bật. Không dừng pve-ha-lrm và pve-ha-crm đồng loạt.

<!-- từ khóa: proxmox ha fencing domino tràn ram overload vm đồng loạt khởi động node dead sập hệ thống ha-manager tắt ha trước khi bảo trì -->
