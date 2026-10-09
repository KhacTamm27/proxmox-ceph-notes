# Proxmox + Ceph command notes

Tài liệu cá nhân: 499 lệnh, 32 nhóm. Lệnh có ⚠ (23 lệnh) là lệnh phá hủy hoặc ảnh hưởng dịch vụ, đọc kỹ trước khi chạy.

**Mindmap tương tác (lọc lệnh, mở thẳng từng mục):** https://KhacTamm27.github.io/proxmox-ceph-notes/

## Cách tìm nhanh

- Mới bắt đầu: mở mindmap, chọn lối đi theo nhu cầu (tìm lệnh, sửa lỗi Proxmox/Ceph, cấu hình network); mở case để đọc triệu chứng, nguyên nhân, các bước và lưu ý.
- Tìm nội dung: gõ từ khóa tiếng Việt hoặc tiếng Anh vào ô tìm kiếm; truy vấn như `storage bị chậm` hoặc `VM crash` có thể hiện quy trình chẩn đoán ban đầu, lệnh đọc trạng thái và cách hiểu dấu hiệu. Trang không chạy lệnh hay truy cập cluster.
- Nhấn `/` để focus tìm kiếm, Enter để tới kết quả, Esc để xóa.
- Tra cứu nhóm lệnh: mở nhóm theo chủ đề; bấm lệnh để copy. Các nhóm Proxmox và Ceph có nhãn màu riêng.
- Mở nhanh qua URL: thêm `#B13` để tới nhóm lệnh (ví dụ RGW), hoặc `?q=scrub` để mở sẵn kết quả tìm kiếm.
- Trên GitHub: nhấn `t` để tìm file theo tên, nhấn `/` để tìm trong repo (gõ `crush`, `radosgw-admin user`).
- Lệnh có ⚠ hoặc hiển thị cảnh báo cần được đọc kỹ trước khi chạy trên cluster thật.

## Case study Ceph (lỗi và cách xử lý)

| Sự cố | Triệu chứng |
|---|---|
| [OSD down hoặc up/down liên tục (flapping)](docs/cases/ceph/osd-down-flapping.md) | ceph -s báo "N osds down", OSD lúc up lúc down, log có "wrongly marked me down" hoặc heartbeat_check no reply. |
| [PG inconsistent / scrub errors](docs/cases/ceph/pg-inconsistent.md) | HEALTH_ERR, "pg x.y is active+clean+inconsistent", "N scrub errors". |
| [Clock skew trên MON (lệch giờ)](docs/cases/ceph/clock-skew.md) | HEALTH_WARN "clock skew detected on mon.X", MON mất quorum chập chờn. |
| [Ceph nearfull / full / pool đầy](docs/cases/ceph/nearfull-full.md) | HEALTH_WARN "N osd(s) nearfull", HEALTH_ERR "full osd(s)", client không ghi được, backfill dừng. |
| [Slow ops / blocked requests](docs/cases/ceph/slow-ops.md) | HEALTH_WARN "N slow ops", VM đơ hoặc IO chậm, "requests are blocked". |
| [Thay đĩa OSD hỏng](docs/cases/ceph/osd-replace-disk.md) | OSD down kéo dài, SMART báo lỗi hoặc dmesg có I/O error, cần thay đĩa vật lý. |
| [Ceph cảnh báo OSD device có nguy cơ hỏng](docs/cases/ceph/osd-device-health-warning.md) | Ceph báo device health hoặc thiết bị có dự đoán tuổi thọ thấp; một OSD vẫn up nhưng SMART/NVMe metrics xấu hoặc thiết bị bị đánh dấu out do dự đoán lỗi. |
| [PG degraded / undersized, recovery chậm](docs/cases/ceph/pg-degraded-recovery.md) | HEALTH_WARN "Degraded data redundancy", "N pgs undersized/degraded", "objects misplaced", recovery chạy lâu. |
| [Large omap objects (thường do bucket index RGW)](docs/cases/ceph/large-omap.md) | HEALTH_WARN "N large omap objects". |
| [RGW/S3 trả 503 hoặc timeout, upload lỗi](docs/cases/ceph/rgw-503.md) | Client S3 nhận 503/timeout, upload thất bại, RGW phản hồi chậm. |
| [MON down, ceph -s treo hoặc mất quorum Ceph](docs/cases/ceph/mon-down.md) | ceph -s đứng treo hoặc báo "1/3 mons down", "mon.X is down". |
| [OSD không lên sau reboot](docs/cases/ceph/osd-wont-start.md) | Sau reboot một số OSD vẫn down, systemctl báo failed hoặc start-limit-hit. |
| [VM treo IO do image RBD (watcher, lock, blocklist)](docs/cases/ceph/rbd-hang.md) | VM đơ hoặc không start vì đĩa RBD, lỗi "image is locked", "timeout" khi mở image. |
| [Cảnh báo PG không được scrub / deep-scrub kịp thời](docs/cases/ceph/deep-scrub-late.md) | HEALTH_WARN "N pgs not deep-scrubbed in time" hoặc "not scrubbed in time". |
| [Cảnh báo too many / too few PGs, chỉnh pg_num](docs/cases/ceph/pg-count.md) | HEALTH_WARN "too many PGs per OSD" hoặc "pool has too few/many pgs". |
| [Mạng Ceph: MTU không khớp, nghẽn hoặc rớt gói](docs/cases/ceph/network-mtu.md) | Slow ops hoặc OSD flapping chỉ liên quan một vài node, ping thường được nhưng IO lớn bị treo. |
| [RGW/S3 trả 403 (AccessDenied, SignatureDoesNotMatch, QuotaExceeded)](docs/cases/ceph/rgw-403.md) | Client S3 nhận 403 dù cluster khỏe: AccessDenied, SignatureDoesNotMatch hoặc QuotaExceeded. |
| [Xem lại Access Key và Secret Key của user S3](docs/cases/ceph/rgw-view-s3-keys.md) | Cần tra lại Access Key/Secret Key để cấu hình client S3 hoặc kiểm tra lỗi xác thực. |
| [Thêm OSD hoặc node mới làm chậm production](docs/cases/ceph/add-osd-throttle.md) | Sau khi thêm OSD hoặc node, VM chậm, nhiều PG backfilling, objects misplaced. |
| [PG down, peering kẹt hoặc unfound objects (mất nhiều OSD)](docs/cases/ceph/pg-down-incomplete.md) | HEALTH_ERR, "N pgs down", pg ở trạng thái down+peering, IO vào một số object bị treo; hoặc "N unfound" (objects unfound). |
| [BLUEFS_SPILLOVER: metadata RocksDB tràn sang đĩa chậm](docs/cases/ceph/bluefs-spillover.md) | HEALTH_WARN "BlueFS spillover detected on N OSD(s)", latency của các OSD HDD tăng. |
| [Cluster đầy khẩn cấp: ghi bị chặn (OSD_FULL), backfill_toofull](docs/cases/ceph/cluster-full-emergency.md) | HEALTH_ERR "full osd(s)", VM không ghi được, PG có backfill_toofull hoặc recovery_toofull nên recovery không chạy. |
| [Latency OSD cao, IOPS thấp do SSD consumer (không có PLP)](docs/cases/ceph/osd-latency-consumer-ssd.md) | ceph osd perf cho commit/apply latency hàng chục đến hàng trăm ms ở một số OSD, VM chậm, thỉnh thoảng slow ops, benchmark cho IOPS rất thấp. |
| [Nâng cấp Ceph trên Proxmox (ví dụ Reef lên Squid)](docs/cases/ceph/ceph-upgrade-pve.md) | Cần nâng cấp phiên bản Ceph mà không làm gián đoạn VM; sau nâng cấp có cảnh báo require-osd-release. |
| [Cờ bảo trì Ceph còn sót sau bảo trì (noout, noscrub, norecover...)](docs/cases/ceph/maintenance-flags-left.md) | HEALTH_WARN "noout,nobackfill,norecover,norebalance,noscrub,nodeep-scrub flag(s) set", PG không recover, cảnh báo scrub quá hạn. |
| [CephFS: MDS failover khi restart hoặc nâng cấp (max_mds lớn hơn 1)](docs/cases/ceph/cephfs-mds-restart.md) | Restart ceph-mds.target hoặc nâng cấp làm CephFS gián đoạn ngắn, trạng thái MDS tạm là replay, reconnect hoặc rejoin. |

## Case study Proxmox cluster (lỗi và cách xử lý)

| Sự cố | Triệu chứng |
|---|---|
| [Cluster Proxmox mất quorum](docs/cases/pve/pve-quorum-lost.md) | GUI báo "cluster not ready - no quorum", /etc/pve chuyển read-only, không start được VM, node hiện đỏ. |
| [Storage dùng chung giữa hai cluster Proxmox gây xung đột lock/VMID](docs/cases/pve/pve-storage-shared-clusters.md) | VM start/migrate hoặc thao tác storage thất bại bất thường; cùng một NFS export, LUN hoặc Ceph pool đang được cấu hình cho hai cluster Proxmox độc lập; VMID có thể trùng. |
| [Bảo trì hoặc reboot một node Proxmox + Ceph](docs/cases/pve/node-maintenance.md) | Cần reboot node để nâng cấp kernel hoặc thay phần cứng mà không làm gián đoạn VM và không kích hoạt rebalance. |
| [VM bị lock (backup/snapshot), không start hoặc migrate được](docs/cases/pve/vm-locked.md) | Báo "VM is locked (backup)" hoặc "(snapshot)", không start, stop, migrate hoặc xóa được. |
| [GUI Proxmox bị đăng xuất liên tục hoặc không đăng nhập được](docs/cases/pve/pve-gui-logout.md) | GUI bị đá ra sau một thời gian ngắn, báo "permission denied" hoặc "invalid ticket", trang tải chậm hoặc treo. |
| [Node Proxmox đầy ổ root, dịch vụ lỗi](docs/cases/pve/pve-disk-full.md) | "No space left on device", dịch vụ không start, không ghi được /etc/pve, GUI lỗi. |
| [Cấu hình mạng Proxmox: OVS/Linux bridge, bond, LACP và VLAN trunk](docs/cases/pve/pve-network-bridge-bond-vlan.md) | VM/CT mất mạng hoặc không nhận VLAN; host mất IP quản trị sau khi sửa /etc/network/interfaces; bond chỉ chạy một link hoặc LACP không lên; VLAN tag/trunk không thông suốt. |
| [Migrate VM thất bại](docs/cases/pve/migrate-fail.md) | Migrate báo lỗi, treo ở một phần trăm nào đó, hoặc không cho chọn node đích. |
| [VM không start được](docs/cases/pve/vm-wont-start.md) | qm start báo lỗi, task lỗi, VM dừng ngay sau khi bật. |
| [Node hoặc VM hiện dấu hỏi (unknown), GUI không cập nhật](docs/cases/pve/pvestatd-unknown.md) | Trong GUI node, VM hoặc storage hiện dấu (?) xám, số liệu không cập nhật dù VM vẫn chạy. |
| [HA: VM không tự chạy lại trên node khác, trạng thái error hoặc fence](docs/cases/pve/ha-no-restart.md) | Node chết nhưng VM HA không tự khởi động ở node khác, hoặc VM HA ở trạng thái error, freeze, fence. |
| [Backup vzdump lỗi hoặc treo](docs/cases/pve/backup-fail.md) | Job backup báo lỗi, chạy rất lâu, hoặc để lại VM bị lock. |
| [local-lvm (thin pool) đầy](docs/cases/pve/lvm-thin-full.md) | local-lvm gần 100%, VM bị I/O error hoặc treo, log có "thin pool ... out of space". |
| [Corosync link chập chờn, retransmit, node tự reboot (HA watchdog)](docs/cases/pve/corosync-flapping.md) | Log corosync có "Retransmit List", knet link down/up, "Token has not been received"; cluster mất quorum rồi phục hồi; các node có HA tự reboot cùng lúc. |
| [Xóa node hỏng và join lại cùng tên (node ma xám trong GUI)](docs/cases/pve/ghost-node-rejoin.md) | Đã pvecm delnode nhưng node vẫn hiện xám trong GUI; cài lại node cùng tên không join được hoặc báo lỗi SSH/chứng chỉ. |
| [Lỗi cfs-lock "got lock request timeout" (pmxcfs, HA, replication)](docs/cases/pve/cfs-lock-timeout.md) | Log có "cfs-lock ... error: got lock request timeout" (từ pvescheduler, pvestatd, ha-crm), tác vụ HA/replication/backup lỗi, GUI báo unknown. |
| [Nâng cấp Proxmox VE 8 lên 9 trong cluster có Ceph](docs/cases/pve/pve-upgrade-8to9.md) | Cần nâng cấp cluster Proxmox đang chạy production (có Ceph, HA) mà không gián đoạn dịch vụ. |
| [Một node chết hẳn (hỏng phần cứng): khôi phục dịch vụ](docs/cases/pve/node-dead-recovery.md) | Một node mất hoàn toàn (không bật lại được), VM trên node đó ngừng, GUI hiện node đỏ, Ceph báo OSD down và PG degraded. |
| [Node dừng: HA khởi động lại đồng loạt VM làm tràn RAM (domino)](docs/cases/pve/ha-domino.md) | Một node dừng hoặc bị fence, VM của nó tự bật lại trên các host còn lại, RAM các host đầy, hệ thống chậm hoặc sập lan sang node khác. |
| [PBS hỏng hoặc tắt: dựng PBS mới nhận lại Datastore S3 (adopt) và restore](docs/cases/pve/pbs-s3-recovery.md) | Máy PBS cũ lỗi phần cứng, cháy, hoặc chủ động tắt, cần khôi phục dữ liệu backup đang nằm trên bucket S3. |
| [LUN iSCSI mới hoặc Volume Group không hiện trên một số node (Shared LVM)](docs/cases/pve/lun-not-visible.md) | Sau khi thêm LUN hoặc mở rộng VG, một số node không thấy thiết bị hoặc không thấy VG, pvesm status báo storage lỗi. |
| [Storage NFS offline hoặc không thêm được vào Proxmox](docs/cases/pve/nfs-storage-offline.md) | Storage NFS hiện dấu hỏi hoặc offline, không thêm được vào Datacenter > Storage, lệnh pvesm status chậm hoặc treo. |
| [PBS S3: ENOENT hoặc Permission denied với cache, không thấy backup](docs/cases/pve/pbs-s3-permission.md) | Tạo hoặc mount datastore S3 báo ENOENT hoặc Permission denied, backup lỗi, hoặc PBS mới không thấy bản backup cũ. |
| [Console VM qua proxy không kết nối (màn hình đen, 401, 403, 404, 502, WebSocket đứt)](docs/cases/pve/console-proxy-fail.md) | Bấm Remote Console trên portal chỉ thấy màn hình đen, báo không kết nối, hoặc F12 > Network thấy vncproxy hoặc vncwebsocket lỗi (401, 403, 404, 502, không lên 101). |
| [PVE host hỏng đĩa boot, không có backup cấu hình: kiểm kê và dựng lại node](docs/cases/pve/pve-host-rebuild-no-config-backup.md) | Node Proxmox không khởi động do hỏng ổ boot, không có bản backup cấu hình node; VM hoặc dịch vụ Ceph trên node cần được khôi phục. |

## Runbook (quy trình thao tác từng bước)

| Runbook | Mục tiêu |
|---|---|
| [Nâng cấp Ceph Quincy 17.2.8 → Reef 18.2.8 → Squid 19.2.4 trên PVE 8.4 (3 node, có CephFS)](docs/runbooks/rb-ceph-upgrade-quincy-reef-squid.md) | Nâng Ceph hai bước liên tiếp (Quincy lên Reef, rồi Reef lên Squid) trên cluster 3 node hyper-converged (mỗi node có MON, MGR, OSD, MDS), PVE giữ nguyên 8.4. Ghi chú gốc dừng ở PVE 8.4 + Squid 19.2.4; bước tiếp theo là pve8to9. |
| [Bảo trì production: tắt HA và đặt cờ bảo trì Ceph trước khi tắt node](docs/runbooks/rb-prod-maintenance.md) | Tắt hoặc reboot node trong môi trường production mà không kích hoạt fencing/HA di chuyển VM đồng loạt, và không để Ceph backfill/recovery không cần thiết. |
| [PBS: tạo Datastore S3 với local cache ZFS và backup từ PVE](docs/runbooks/rb-pbs-s3-datastore.md) | Dùng một bucket S3 (nhà cung cấp S3-compatible) làm datastore của PBS 4.x, có vùng đệm local cache trên ZFS, rồi thêm vào PVE và backup thử. |
| [Nâng cấp một node Proxmox VE từ 5.4 lên 8.x (qua 6, 7, 8) kèm ZFS](docs/runbooks/rb-pve5-to-8-single.md) | Nâng một node đơn Proxmox rất cũ (5.4, Debian stretch) lên 8.x theo chuỗi 5 lên 6 lên 7 lên 8, rồi import lại các zpool dữ liệu. |
| [SAN iSCSI + Shared LVM cho cluster Proxmox, và mở rộng dung lượng online (pvmove)](docs/runbooks/rb-san-iscsi-shared-lvm.md) | Cho 3 node Proxmox cùng đăng nhập một LUN iSCSI và dùng chung một Volume Group (Shared LVM) để chia volume cho VM; sau đó mở rộng dung lượng không mất dữ liệu, không downtime. |
| [NAS NFS làm storage dùng chung cho cluster Proxmox](docs/runbooks/rb-nas-nfs-storage.md) | Cho 3 node Proxmox mount chung một thư mục xuất từ NFS server, chứa trực tiếp file .qcow2 hoặc .raw của VM. Dễ triển khai, phù hợp lab hoặc tải vừa phải. |
| [Cấu hình Nginx proxy console cho VM Proxmox (noVNC qua portal)](docs/runbooks/rb-console-proxy-nginx.md) | Cho kỹ thuật hoặc khách hàng thao tác console VM ngay trên portal hoặc trang quản lý dịch vụ mà không phải mở thẳng giao diện Proxmox. Portal gửi URL kèm tiền tố tới Nginx proxy, Nginx bỏ tiền tố, rewrite đường dẫn API rồi chuyển xuống đúng node Proxmox (cổng 8006); mỗi node ứng với một cổng riêng trên proxy. |
| [Gỡ lỗi console: lấy ticket qua API, áp cookie, mở URL chuẩn rồi kiểm tra bằng F12](docs/runbooks/rb-console-ticket-debug.md) | Kiểm tra từng chặng của đường console (Proxmox, proxy, trình duyệt) mà không cần portal: tự lấy ticket đăng nhập, áp vào trình duyệt, mở URL chuẩn qua proxy và dùng DevTools (F12) để thấy chặng nào lỗi. |
| [ZFS: chọn RAID/vdev và tạo pool cho Proxmox](docs/runbooks/rb-zfs-vdev-layout.md) | Chọn bố cục ZFS phù hợp workload VM/CT, tạo pool mới an toàn và thêm pool làm storage trong Proxmox VE. |
| [ZFS RAIDZ: mở rộng vdev bằng cách gắn thêm disk](docs/runbooks/rb-zfs-raidz-expansion.md) | Mở rộng một RAIDZ vdev hiện có bằng tính năng RAIDZ expansion của OpenZFS khi hệ thống và pool hỗ trợ. |
| [ZFS: thêm hoặc gỡ L2ARC cache và hot spare](docs/runbooks/rb-zfs-cache-spare.md) | Quản lý thiết bị cache đọc L2ARC hoặc hot spare cho ZFS pool mà không nhầm với disk dữ liệu, SLOG hay backup. |
| [Proxmox boot ZFS mirror: kiểm tra trước khi thay disk rpool](docs/runbooks/rb-zfs-rpool-replace.md) | Thu thập thông tin và chuẩn bị an toàn cho việc thay disk trong rpool mirror của Proxmox VE. |
| [Proxmox ZFS replication: cấu hình và kiểm thử khôi phục VM](docs/runbooks/rb-pve-zfs-replication.md) | Cấu hình replication ZFS định kỳ giữa các node trong cùng cluster PVE và kiểm thử khả năng khôi phục mà không tạo VM trùng hoặc gây split-brain. |
| [P2V Linux/Ubuntu: chuyển disk vật lý thành VM trên Proxmox](docs/runbooks/rb-p2v-linux.md) | Tạo bản disk image nhất quán của máy Linux vật lý, import vào Proxmox VE và xác nhận VM mới boot/hoạt động trước khi dừng máy nguồn. |
| [P2V Windows: Disk2vhd, import VHDX và cài driver Proxmox](docs/runbooks/rb-p2v-windows.md) | Chuyển một máy Windows vật lý sang VM Proxmox bằng VHD/VHDX, giữ máy nguồn và kiểm thử bản sao trước khi cutover. |
| [V2V Hyper-V sang Proxmox bằng StarWind V2V Converter](docs/runbooks/rb-v2v-hyperv.md) | Chuyển VM từ Hyper-V sang Proxmox, giữ nguyên bản nguồn và kiểm thử VM đích trước khi chuyển dịch vụ. |
| [V2V VMware ESXi sang Proxmox bằng StarWind V2V Converter](docs/runbooks/rb-v2v-esxi.md) | Chuyển VM từ ESXi sang Proxmox bằng converter, kiểm thử trong môi trường cô lập và giữ nguyên nguồn để rollback. |
| [Di chuyển VM giữa hai cluster Proxmox bằng remote migration](docs/runbooks/rb-pve-cross-cluster-migrate.md) | Di chuyển VM giữa hai cluster PVE độc lập bằng remote migration, kiểm soát quyền API, mapping network/storage và cutover. |
| [Xóa node Proxmox khỏi cluster an toàn (VM, HA và Ceph)](docs/runbooks/rb-pve-remove-node.md) | Gỡ một node PVE khỏi cluster sau khi đã xử lý workload, HA và mọi dịch vụ Ceph gắn với node đó. |

## Script tiện ích

| Script | Mục đích |
|---|---|
| [Kiểm tra tổng hợp host, storage và network/VLAN toàn cluster](docs/scripts/pve-cluster-inventory.md) | Tổng hợp node/host, datastore cluster, trạng thái và dung lượng datastore theo từng node, cùng interface VLAN và bridge VLAN-aware để kiểm tra cấu hình toàn cluster. Xuất kết quả ra màn hình và các file CSV. |
| [Liệt kê VLAN tag/trunks đang dùng trên toàn cluster](docs/scripts/list-vlan-tags.md) | Tổng hợp các VLAN ID có tag hoặc trunks trong cấu hình VM/CT trên mọi node Proxmox, giúp kiểm tra VLAN nào đang được sử dụng trước khi cấu hình switch hoặc bridge. |
| [Liệt kê cổng mạng vật lý đang UP (1Gb / 10Gb) trên mọi node cluster](docs/scripts/list-up-ports.md) | Kiểm tra nhanh card mạng vật lý nào đang UP và đạt tốc độ nào trên từng node của cluster (đọc danh sách node và IP từ /etc/pve/.members), để phát hiện cổng rớt tốc độ, đứt cáp hoặc cắm nhầm cổng. |
| [Menu Stop / Start / Status HA (pve-ha-lrm, pve-ha-crm) trên toàn cluster](docs/scripts/ha-menu.md) | Tắt hoặc bật HA đồng loạt trên mọi node online đúng thứ tự khi bảo trì production (stop LRM trước rồi CRM; start CRM trước, chờ bầu master, rồi LRM) thay vì gõ tay từng node. Tương ứng bước tắt HA trong runbook bảo trì production. |

## Proxmox host

| ID | Nhóm | Lệnh | Gồm |
|---|---|---:|---|
| A1 | [System and node](docs/proxmox/A01-system-and-node.md) | 21 | Version, Load, Time, Services, Node, Certificates, Upgrade, Kernel |
| A2 | [Cluster and corosync](docs/proxmox/A02-cluster-and-corosync.md) | 16 | Status, Links, Logs, Config, Membership, Quorum, Recovery |
| A3 | [Virtual machines (qm)](docs/proxmox/A03-virtual-machines-qm.md) | 39 | Inspect, Power, Create, Config, Snapshot, Migration, Guest agent, Console, Cloud-init, Import |
| A4 | [Containers (pct) and templates](docs/proxmox/A04-containers-pct-and-templates.md) | 19 | Inspect, Power, Access, Create, Config, Snapshot, Migration, Delete, Templates |
| A5 | [Storage (pvesm)](docs/proxmox/A05-storage-pvesm.md) | 11 | Status, Config, Scan, Volume |
| A6 | [Backup and restore](docs/proxmox/A06-backup-and-restore.md) | 16 | vzdump, Restore, Jobs, PBS client, PBS server (on PBS host), PBS server |
| A7 | [High availability and replication](docs/proxmox/A07-high-availability-and-replication.md) | 14 | Status, Resources, Groups, Move, Maintenance, Services, Replication |
| A8 | [Network](docs/proxmox/A08-network.md) | 23 | Interfaces, Bridge, Bond, Config, NIC, MTU test, Throughput, Sockets, Capture, Path, Neighbors, OVS, QoS |
| A9 | [Firewall](docs/proxmox/A09-firewall.md) | 5 | Status, Rules, Control |
| A10 | [Disks and filesystems](docs/proxmox/A10-disks-and-filesystems.md) | 17 | Inventory, Usage, NVMe, SMART, LVM, ZFS, IO, Benchmark, Wipe |
| A11 | [Hardware and performance](docs/proxmox/A11-hardware-and-performance.md) | 13 | CPU, Memory, Load, Sensors, BMC, Kernel log |
| A12 | [Access control (pveum)](docs/proxmox/A12-access-control-pveum.md) | 8 | Users, Roles, Permissions, Tokens, Realms |
| A13 | [Tasks, logs and API](docs/proxmox/A13-tasks-logs-and-api.md) | 10 | Tasks, Logs, API |
| A14 | [Ceph management from Proxmox (pveceph)](docs/proxmox/A14-ceph-management-from-proxmox-pveceph.md) | 16 | Install, MON, MGR, OSD, Pool, CephFS, Services, Cleanup |

## Ceph

| ID | Nhóm | Lệnh | Gồm |
|---|---|---:|---|
| B1 | [Health and status](docs/ceph/B01-health-and-status.md) | 14 | Overview, Health, Capacity, Versions, Log, Crash, Time, Report |
| B2 | [MON](docs/ceph/B02-mon.md) | 8 | Status, Quorum, Admin socket, Maintenance, Features, Protocol, Map |
| B3 | [MGR and modules](docs/ceph/B03-mgr-and-modules.md) | 12 | Status, Control, Modules, Balancer, IO, Progress |
| B4 | [OSD status](docs/ceph/B04-osd-status.md) | 22 | Tree, Usage, State, Info, Device health, Perf, Ratios, Blocklist |
| B5 | [OSD flags and maintenance](docs/ceph/B05-osd-flags-and-maintenance.md) | 15 | Flags, Per subtree, Safety, State, Weight |
| B6 | [OSD lifecycle and devices](docs/ceph/B06-osd-lifecycle-and-devices.md) | 15 | Inventory, Create, Replace, Remove, Wipe, Service, BlueStore, Maintenance, Class |
| B7 | [OSD daemon and performance (admin socket)](docs/ceph/B07-osd-daemon-and-performance-admin-socket.md) | 9 | Ops, Perf, Config, Bench, Heartbeat |
| B8 | [CRUSH map](docs/ceph/B08-crush-map.md) | 19 | View, Rules, Buckets, Map file |
| B9 | [Pools](docs/ceph/B09-pools.md) | 18 | View, Create, Settings, Autoscale, Quota, Rename, Delete, Usage |
| B10 | [Placement groups](docs/ceph/B10-placement-groups.md) | 16 | Summary, List, Mapping, Detail, Scrub, Repair, Priority, Upmap |
| B11 | [Recovery, scrub and config tuning](docs/ceph/B11-recovery-scrub-and-config-tuning.md) | 11 | Config, Backfill, Recovery, mClock, Scrub |
| B12 | [RBD (VM disks)](docs/ceph/B12-rbd-vm-disks.md) | 26 | List, Info, Snapshot, Clone, Copy, Resize, Space, Trash, Delete, Perf, Bench, Mapping |
| B13 | [RGW and S3 (radosgw-admin)](docs/ceph/B13-rgw-and-s3-radosgw-admin.md) | 33 | Service, Users, Keys, Subuser, Quota, Buckets, Reshard, Usage, Lifecycle, GC, Topology, Index pool |
| B14 | [CephFS](docs/ceph/B14-cephfs.md) | 8 | Status, Create, Subvolume, Failover, Delete |
| B15 | [Authentication (cephx)](docs/ceph/B15-authentication-cephx.md) | 6 | List, Show, Create, Change, Delete |
| B16 | [Benchmarks and low-level rados](docs/ceph/B16-benchmarks-and-low-level-rados.md) | 12 | Bench, Objects, Omap |
| B17 | [Upgrade and compatibility](docs/ceph/B17-upgrade-and-compatibility.md) | 8 | Versions, Release, Clients, Pre-upgrade, Post-upgrade |
| B18 | [Troubleshooting shortlist](docs/ceph/B18-troubleshooting-shortlist.md) | 19 | HEALTH_WARN, Slow ops, OSD flapping, PGs stuck, Undersized, Nearfull, Large omap, Clock skew, MON down, Client hang |

## Cập nhật tài liệu

- `data/commands.json`: nhóm → nhóm con → `{c: lệnh, p: mô tả, d: nguy hiểm?}`.
- `data/vi.json`: mô tả tiếng Việt và từ khóa, khóa là đúng chuỗi lệnh trong commands.json: `"lệnh": ["mô tả", "từ khóa"]`.
- `data/cases.json`: các case study (triệu chứng, nguyên nhân, các bước, lưu ý).
- `data/triage.json`: hướng dẫn chẩn đoán ban đầu theo mô tả tự nhiên (ví dụ VM crash, storage chậm), gồm lệnh chỉ đọc, dấu hiệu cần xem và case liên quan.
- `data/scripts.json` và thư mục `tools/`: script tiện ích (siêu dữ liệu trong JSON, mã nguồn `.sh` hoặc `.py` trong `tools/`).

Sau khi sửa, chạy:

```bash
python3 scripts/build.py --repo KhacTamm27/proxmox-ceph-notes
```

Lệnh trên sinh lại README này, toàn bộ `docs/**/*.md` và `docs/index.html`.
