import asyncio
from pysnmp.hlapi.v3arch.asyncio import *


# ============================================================
# SETTINGS
# ============================================================

COMMUNITY = "public"

switches = [
    "10.0.2.11",
    "10.0.2.12",
    "10.0.2.13",
    "10.0.2.14",
    "10.0.2.15",
    "10.0.2.16",
    "10.0.2.17",
    "10.0.2.18",
    "10.0.2.19",
    "10.0.2.21",
    "10.0.2.22",
    "10.0.2.23",
    "10.0.2.25",
    "10.0.2.26",
    "10.0.2.29",
    "10.0.2.31",
    "10.0.2.32",
    "10.0.2.33",
    "10.0.2.34",
    "10.0.2.35",
    "10.0.2.36",
    "10.0.2.37",
    "10.0.2.41",
    "10.0.2.42",
    "10.0.2.43",
    "10.0.2.44",
    "10.0.2.45",
    "10.0.2.46",
    "10.0.2.48",
    "10.0.2.49",
    "10.0.2.51",
    "10.0.2.53",
    "10.0.3.11",
    "10.0.3.12",
    "10.0.3.21",
    "10.0.3.24",
    "10.0.3.31",
    "10.0.3.42",
    "10.0.3.51",
    "10.0.3.53",
    "10.0.4.14",
    "10.0.0.20",
    "10.0.0.21",
    "10.0.0.22",
    "10.0.0.23",
    "10.0.0.24",
    "10.0.0.25",
    "10.0.0.26",
    "10.0.0.27",
    "10.0.0.28",
    "10.0.0.29",
    "10.0.1.12",
    "10.0.1.13",
    "10.0.1.14",
    "10.0.1.15",
    "10.0.1.16",
    "10.0.1.17",
    "10.0.1.18",
    "10.0.1.19",
    "10.0.1.21",
    "10.0.1.22",
    "10.0.1.23",
    "10.0.1.24",
    "10.0.1.25",
    "10.0.1.26",
    "10.0.1.27",
    "10.0.1.28",
    "10.0.1.29",
    "10.0.1.31",
    "10.0.1.32",
    "10.0.1.33",
    "10.0.1.34",
    "10.0.1.35",
    "10.0.1.36",
    "10.0.1.37",
    "10.0.1.38",
    "10.0.1.39",
    "10.0.1.41",
    "10.0.1.42",
    "10.0.1.43",
    "10.0.1.44",
    "10.0.1.45",
    "10.0.1.46",
    "10.0.1.47",
    "10.0.1.48",
    "10.0.1.49",
    "10.0.1.51",
    "10.0.1.53"
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