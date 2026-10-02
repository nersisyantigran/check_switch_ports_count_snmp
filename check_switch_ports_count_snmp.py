import asyncio
from pysnmp.hlapi.v3arch.asyncio import *


# ============================================================
# SETTINGS
# ============================================================

COMMUNITY = "public"

switches = [
    # ips
]

# ============================================================
# OID
# ============================================================
 
# IF-MIB::ifOperStatus
#
# 1 = up
# 2 = down
#
IF_OPER_STATUS = "1.3.6.1.2.1.2.2.1.8"


# ============================================================
# SNMP WALK
# ============================================================

async def get_up_ports(ip):

    snmp_engine = SnmpEngine()

    try:

        transport = await UdpTransportTarget.create(
            (ip, 161),
            timeout=2,
            retries=1
        )

        up_ports = []

        async for (
            error_indication,
            error_status,
            error_index,
            var_binds
        ) in walk_cmd(
            snmp_engine,

            CommunityData(
                COMMUNITY,
                mpModel=1
            ),

            transport,

            ContextData(),

            ObjectType(
                ObjectIdentity(IF_OPER_STATUS)
            ),

            lexicographicMode=False
        ):

            if error_indication:
                print(f"SNMP error: {error_indication}")
                return None

            if error_status:
                print(f"SNMP error: {error_status}")
                return None

            for oid, value in var_binds:

                oid_string = str(oid)

                # Последнее число = ifIndex
                if_index = int(
                    oid_string.split(".")[-1]
                )

                status = int(value)

                # ==================================================
                # DGS-3000-26TC
                #
                # Только физические порты 1-26
                # ==================================================

                if 1 <= if_index <= 26:

                    # 1 = UP
                    if status == 1:

                        up_ports.append(if_index)

        return sorted(up_ports)

    except Exception as e:

        print(f"Error on {ip}: {e}")
        return None

    finally:

        snmp_engine.close_dispatcher()


# ============================================================
# MAIN
# ============================================================

async def main():

    print()
    print("=" * 60)
    print("CHECKING DGS-3000-26TC SWITCHES")
    print("=" * 60)
    print()

    found = []

    for ip in switches:

        print(
            f"Checking {ip} ...",
            end=" ",
            flush=True
        )

        up_ports = await get_up_ports(ip)

        if up_ports is None:

            print("SNMP ERROR")
            continue

        print(
            f"{len(up_ports)} UP ports"
        )

        # ====================================================
        # Нам нужны только switch с ОДНИМ UP портом
        # ====================================================

        if len(up_ports) == 1:

            found.append(
                (
                    ip,
                    up_ports[0]
                )
            )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    print()
    print()

    print("=" * 60)
    print("SWITCHES WITH EXACTLY ONE UP PORT")
    print("=" * 60)

    if not found:

        print("No switches found.")

    else:

        print(
            f"{'IP Address':<20} {'UP Port':<10}"
        )

        print("-" * 60)

        for ip, port in found:

            print(
                f"{ip:<20} {port:<10}"
            )

    print("-" * 60)

    print(
        f"Found: {len(found)} switches"
    )

    print()


# ============================================================
# RUN
# ============================================================

asyncio.run(main())