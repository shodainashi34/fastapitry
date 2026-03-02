const get_data_buitton = document.getElementById("get_data")

async function get_data() {

    try {
        const res = await fetch("http://127.0.0.1:8000/vehicles", {
            method: "GET"
        })

        if (!res.ok){
            const text = await res.text()
            console.log("通信エラー", text, res.status)
            return
        }

        const data = await res.json()
        console.log("通信成功", data)
        data.forEach((data) => {
            console.log(data)
        })
    }catch(err){
        console.log(err)
        return
    }
}

get_data_buitton.addEventListener("click", get_data)

const input_vehicleid = document.getElementById("vehicle_id")
const vehicle_send_button = document.getElementById("vehicleid_send")

async function send_vehicleid() {
    try{
        const res = await fetch(`http://127.0.0.1:8000/vehicles/${input_vehicleid.value}/checks`,{
            method: "GET"
        })

        if (!res.ok){
        const text = await res.text()
        console.log("通信不良", text, res.status)
        return
        }

        const data = await res.json()
        console.log("通信完了",data)
    }catch(err){
        console.log("通信不良",err)
        return
    }
}

vehicle_send_button.addEventListener("click", send_vehicleid)