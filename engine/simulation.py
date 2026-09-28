import random

import numpy as np
import simpy


# ============================================================
# HELPERS
# ============================================================

def _normalize_distribution(name, default="exponential"):
    """
    Menormalkan nama distribusi agar konsisten.
    """

    if name is None:
        return default

    value = str(name).strip().lower()

    aliases = {
        "exp": "exponential",
        "exponential": "exponential",

        # Poisson arrival process memiliki
        # exponential inter-arrival time.
        "poisson": "exponential",

        "constant": "deterministic",
        "fixed": "deterministic",
        "deterministic": "deterministic",
    }

    return aliases.get(
        value,
        value,
    )


def _validate_params(params, name):
    """
    Memastikan *_params berbentuk dictionary.
    """

    if params is None:
        return {}

    if not isinstance(params, dict):
        raise ValueError(
            f"{name} harus berupa dictionary"
        )

    return params


# ============================================================
# SIMULATE QUEUE
# ============================================================

def simulate_queue(
    arrival_rate,
    service_time,
    staff,
    operating_hours,
    seed=None,
    arrival_distribution="exponential",
    service_distribution="exponential",
    arrival_params=None,
    service_params=None,
):
    """
    Menjalankan SATU kali simulasi antrian
    untuk satu hari operasional.

    Parameters
    ----------
    arrival_rate : float
        Rata-rata pelanggan datang per JAM.

    service_time : float
        Rata-rata waktu layanan satu pelanggan,
        dalam MENIT.

    staff : int
        Jumlah staf / loket aktif.

    operating_hours : float
        Lama operasional dalam JAM.

    seed : int | str | None
        Seed random generator.

    arrival_distribution : str
        Distribusi inter-arrival time.

        Saat ini:
        - "exponential"
        - "poisson" -> diperlakukan sebagai
          exponential inter-arrival time
        - "deterministic"

    service_distribution : str
        Distribusi service duration.

        Saat ini:
        - "exponential"
        - "deterministic"

    arrival_params : dict | None
        Parameter tambahan untuk distribusi arrival.
        Disediakan agar kompatibel dengan statistics.py.

    service_params : dict | None
        Parameter tambahan untuk distribusi service.
        Disediakan agar kompatibel dengan statistics.py.

    Returns
    -------
    list[dict]

        Satu dictionary per pelanggan:

        {
            "id": ...,
            "arrival": ...,
            "start": ...,
            "end": ...
        }

        Semua waktu dalam MENIT.
    """


    # ========================================================
    # BASIC INPUT CONVERSION
    # ========================================================

    arrival_rate = float(
        arrival_rate
    )

    service_time = float(
        service_time
    )

    operating_hours = float(
        operating_hours
    )

    staff_float = float(
        staff
    )


    # ========================================================
    # BASIC VALIDATION
    # ========================================================

    if arrival_rate <= 0:
        raise ValueError(
            "arrival_rate harus lebih dari 0"
        )

    if service_time <= 0:
        raise ValueError(
            "service_time harus lebih dari 0"
        )

    if operating_hours <= 0:
        raise ValueError(
            "operating_hours harus lebih dari 0"
        )

    if (
        staff_float < 1
        or not staff_float.is_integer()
    ):
        raise ValueError(
            "staff harus bilangan bulat minimal 1"
        )


    staff = int(
        staff_float
    )


    # ========================================================
    # MODEL CONFIG
    # ========================================================

    arrival_distribution = (
        _normalize_distribution(
            arrival_distribution
        )
    )

    service_distribution = (
        _normalize_distribution(
            service_distribution
        )
    )


    arrival_params = (
        _validate_params(
            arrival_params,
            "arrival_params",
        )
    )

    service_params = (
        _validate_params(
            service_params,
            "service_params",
        )
    )


    # ========================================================
    # SUPPORTED DISTRIBUTIONS
    # ========================================================

    supported_arrivals = {
        "exponential",
        "deterministic",
    }

    supported_services = {
        "exponential",
        "deterministic",
    }


    if (
        arrival_distribution
        not in supported_arrivals
    ):
        raise ValueError(
            "arrival_distribution "
            f"'{arrival_distribution}' "
            "belum didukung oleh simulate_queue(). "
            "Distribusi yang didukung saat ini: "
            "exponential, deterministic."
        )


    if (
        service_distribution
        not in supported_services
    ):
        raise ValueError(
            "service_distribution "
            f"'{service_distribution}' "
            "belum didukung oleh simulate_queue(). "
            "Distribusi yang didukung saat ini: "
            "exponential, deterministic."
        )


    # ========================================================
    # RANDOM GENERATORS
    # ========================================================

    if seed is None:

        arrival_rng = random.Random()
        service_rng = random.Random()

    else:

        arrival_rng = random.Random(
            f"arrival-{seed}"
        )

        service_rng = random.Random(
            f"service-{seed}"
        )


    # ========================================================
    # TIME PARAMETERS
    # ========================================================

    closing_time = (
        operating_hours
        * 60
    )


    arrival_rate_per_min = (
        arrival_rate
        / 60
    )


    service_rate_per_min = (
        1
        / service_time
    )


    mean_interarrival = (
        1
        / arrival_rate_per_min
    )


    # ========================================================
    # DISTRIBUTION SAMPLERS
    # ========================================================

    def sample_interarrival():
        """
        Menghasilkan jarak antar kedatangan
        dalam menit.
        """

        if (
            arrival_distribution
            == "exponential"
        ):

            return (
                arrival_rng.expovariate(
                    arrival_rate_per_min
                )
            )


        if (
            arrival_distribution
            == "deterministic"
        ):

            return mean_interarrival


        raise RuntimeError(
            "Unsupported arrival distribution"
        )


    def sample_service_time():
        """
        Menghasilkan service duration
        dalam menit.
        """

        if (
            service_distribution
            == "exponential"
        ):

            return (
                service_rng.expovariate(
                    service_rate_per_min
                )
            )


        if (
            service_distribution
            == "deterministic"
        ):

            return service_time


        raise RuntimeError(
            "Unsupported service distribution"
        )


    # ========================================================
    # SIMPY ENVIRONMENT
    # ========================================================

    env = simpy.Environment()


    counters = simpy.Resource(
        env,
        capacity=staff,
    )


    records = []


    # ========================================================
    # CUSTOMER PROCESS
    # ========================================================

    def customer(
        customer_id
    ):

        arrival = env.now


        duration = (
            sample_service_time()
        )


        with counters.request() as req:

            yield req


            start = env.now


            yield env.timeout(
                duration
            )


        records.append(
            {
                "id":
                    customer_id,

                "arrival":
                    float(arrival),

                "start":
                    float(start),

                "end":
                    float(env.now),
            }
        )


    # ========================================================
    # ARRIVAL PROCESS
    # ========================================================

    def arrival_process():

        customer_id = 0


        while True:

            gap = (
                sample_interarrival()
            )


            yield env.timeout(
                gap
            )


            # Tidak membuat customer baru
            # sesudah jam tutup.
            if (
                env.now
                >= closing_time
            ):
                break


            customer_id += 1


            env.process(
                customer(
                    customer_id
                )
            )


    # ========================================================
    # RUN SIMULATION
    # ========================================================

    env.process(
        arrival_process()
    )


    # env.run() tetap berjalan sampai semua
    # pelanggan yang datang sebelum closing
    # selesai dilayani.
    env.run()


    # ========================================================
    # SORT RECORDS
    # ========================================================

    records.sort(
        key=lambda record:
            record["id"]
    )


    return records


# ============================================================
# CALCULATE METRICS
# ============================================================

def calculate_metrics(
    records,
    staff,
    operating_hours,
):
    """
    Mengubah catatan mentah dari simulate_queue()
    menjadi metrik ringkasan.

    Semua waktu dalam MENIT,
    kecuali throughput_per_hour.
    """


    staff = int(
        staff
    )

    operating_hours = float(
        operating_hours
    )


    if staff < 1:
        raise ValueError(
            "staff harus minimal 1"
        )


    if operating_hours <= 0:
        raise ValueError(
            "operating_hours harus lebih dari 0"
        )


    closing = (
        operating_hours
        * 60
    )


    # ========================================================
    # EMPTY RESULT
    # ========================================================

    if not records:

        return {
            "customers_served":
                0,

            "completed_by_closing":
                0,

            "throughput_per_hour":
                0.0,

            "avg_wait":
                0.0,

            "max_wait":
                0.0,

            "p90_wait":
                0.0,

            "avg_queue_length":
                0.0,

            "max_queue_length":
                0,

            "utilization":
                0.0,

            "overtime_minutes":
                0.0,
        }


    # ========================================================
    # WAITING TIME
    # ========================================================

    waits = np.array(
        [
            (
                record["start"]
                - record["arrival"]
            )

            for record
            in records
        ],

        dtype=float,
    )


    # ========================================================
    # COMPLETED BY CLOSING
    # ========================================================

    completed = sum(
        1

        for record
        in records

        if (
            record["end"]
            <= closing
        )
    )


    # ========================================================
    # QUEUE AREA
    #
    # Total waiting-minutes customer
    # selama jam operasi.
    # ========================================================

    queue_area = sum(

        max(
            0.0,

            min(
                record["start"],
                closing,
            )
            -
            min(
                record["arrival"],
                closing,
            )
        )

        for record
        in records
    )


    # ========================================================
    # MAX QUEUE LENGTH
    # ========================================================

    events = []


    for record in records:

        if (
            record["start"]
            > record["arrival"]
        ):

            events.append(
                (
                    record["arrival"],
                    +1,
                )
            )


            events.append(
                (
                    record["start"],
                    -1,
                )
            )


    # Jika waktu event sama,
    # -1 diproses sebelum +1.
    events.sort(
        key=lambda item:
            (
                item[0],
                item[1],
            )
    )


    current_queue = 0

    max_queue = 0


    for _, change in events:

        current_queue += change


        max_queue = max(
            max_queue,
            current_queue,
        )


    # ========================================================
    # UTILIZATION
    # ========================================================

    busy_time = sum(

        max(
            0.0,

            min(
                record["end"],
                closing,
            )
            -
            min(
                record["start"],
                closing,
            )
        )

        for record
        in records
    )


    available_server_minutes = (
        staff
        * closing
    )


    utilization = (

        busy_time
        / available_server_minutes

        if (
            available_server_minutes
            > 0
        )

        else 0.0
    )


    # ========================================================
    # OVERTIME
    # ========================================================

    last_end = max(
        record["end"]

        for record
        in records
    )


    overtime_minutes = max(
        0.0,
        last_end - closing,
    )


    # ========================================================
    # FINAL METRICS
    # ========================================================

    return {

        "customers_served":
            int(
                len(records)
            ),

        "completed_by_closing":
            int(
                completed
            ),

        "throughput_per_hour":
            float(
                completed
                / operating_hours
            ),


        "avg_wait":
            float(
                waits.mean()
            ),

        "max_wait":
            float(
                waits.max()
            ),

        "p90_wait":
            float(
                np.percentile(
                    waits,
                    90,
                )
            ),


        "avg_queue_length":
            float(
                queue_area
                / closing
            ),

        "max_queue_length":
            int(
                max_queue
            ),


        "utilization":
            float(
                utilization
            ),


        "overtime_minutes":
            float(
                overtime_minutes
            ),
    }


# ============================================================
# MANUAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "QueueWise simulation test\n"
    )


    for staff_count in (
        2,
        3,
        4,
    ):

        records = simulate_queue(

            arrival_rate=40,

            service_time=3,

            staff=staff_count,

            operating_hours=8,

            seed=42,

            arrival_distribution=
                "exponential",

            service_distribution=
                "exponential",

            arrival_params={},

            service_params={},
        )


        metrics = calculate_metrics(
            records,
            staff_count,
            8,
        )


        print(
            f"{staff_count} staff"
        )


        print(
            "  customers        :",
            metrics[
                "customers_served"
            ],
        )


        print(
            "  avg wait         :",
            f"{metrics['avg_wait']:.2f} min",
        )


        print(
            "  max wait         :",
            f"{metrics['max_wait']:.2f} min",
        )


        print(
            "  utilization      :",
            f"{metrics['utilization'] * 100:.1f}%",
        )


        print(
            "  throughput       :",
            f"{metrics['throughput_per_hour']:.1f} customers/hour",
        )


        print(
            "  overtime         :",
            f"{metrics['overtime_minutes']:.1f} min",
        )


        print()