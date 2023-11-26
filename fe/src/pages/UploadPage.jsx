import React, { useState } from 'react';
import axios from 'axios';
import Button from '@mui/material/Button';
import { TextField } from '@mui/material';
import CircularProgress from '@material-ui/core/CircularProgress';
import { Divider } from '@mui/material';

const UploadPage = () => {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [step, setStep] = useState(1);
  const [file, setFile] = useState(null)
  const [address, setAddress] = useState('');
  const [response, setResponse] = useState({type: 'Историческое', photo: null, objects: [{desc: "Кондиционер без решетки (п.5.5)", solution: "повесить решетку или убрать"}]});
  const [processedImage1, setProcessedImage1] = useState(null);
  const [processedImage2, setProcessedImage2] = useState(null);

  const handleUpload = (e) => {
    const file = e.target.files[0];
    setFile(file)
    const reader = new FileReader();

    reader.onloadend = () => {
      setUploadedImage(reader.result);
      setStep(2)
    };

    if (file) {
      reader.readAsDataURL(file);
    }
  };


  const handleAnalyze = async () => {
    const formData = new FormData();
    formData.append('image', file);
    setStep(3)
    
    const response1 = await axios.post('http://127.0.0.1:5100/owl', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    setResponse(response1)
    setProcessedImage1(response1.data.image)
    setStep(4)

    const response2 = await axios.post('http://127.0.0.1:5100/sd', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    setProcessedImage2(response2.data.image)
  };


  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh'}}>
      {step === 1 ? (
        <label htmlFor="upload-image">
          <Button variant="contained" component="span"
          style={{ borderRadius: 0, boxShadow: 'none', 
                    width: '52vw', height: '14vh', 
                    fontSize: '2em', textTransform: 'none',
                    background: '#282828'}}>
              Загрузите фото
          </Button>
          <input id="upload-image" type="file" accept="image/*" hidden onChange={handleUpload} />
        </label>
      ) : (<div/>)}
      {step === 2 ? (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
          <img src={uploadedImage} alt="Uploaded" style={{ height: '40vh' }} />
          <TextField label="Адрес..." variant="outlined" style={{ marginTop: '3em', color: "#282828", borderRadius: 0 }}
            value={address}
            onChange={(event) => {setAddress(event.target.value)}}
          />
          <Button variant="contained" style={{ borderRadius: 0, boxShadow: 'none', 
                  width: '30vw', height: '10vh', 
                  fontSize: '2em', textTransform: 'none',
                  background: '#282828', marginTop: '2em'}}
                  onClick={handleAnalyze}>
            Проанализировать
          </Button>
        </div>
      ) : (<div/>)}
      {step === 3 ? (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
          <span style={{ marginBottom: "2em" }}>
            Обрабатываем фотографию...
          </span>
          <CircularProgress />
        </div>
      ) : (<div/>)}
      {step === 4 ? (
        <div style={{ display: 'flex' }}>
          <div style={{ width: '50%' }}>
            {processedImage1 ? <img src={processedImage1} alt="first" style={{ height: '45vh', marginBottom: '2em' }} /> : <CircularProgress />}
            {/* <h3 style={{ height: '1vh', marginBottom: '2em' }}>Исправленный вариант</h3> */}
            {processedImage2 ? <img src={processedImage2} alt="second" style={{ height: '45vh' }} /> : <CircularProgress />}
          </div>
          <div style={{ width: '50%', verticalAlign: 'bottom' }}>
            <h1>{address ? 'Здание на ' + address : 'Адрес не указан :('}</h1>
            <span style={{ border: 'solid 2px black', padding: '0.5em' }}>{response.type}</span>
            <h1 style={{ paddingTop: '2em' }}>Список несоответствий: </h1>
            <ol style={{ fontSize: '1.5em', paddingLeft: '2em' }}>
              {response.objects.map((e, index) => {
                  return (
                    <div>
                      <li>
                        <p>{e.desc}</p>
                        <p>→ {e.solution}</p>
                        <Divider />
                      </li>
                    </div>
                  )
                })
              }
            </ol>
            <span style={{ border: 'solid 2px #818181', padding: '0.5em', color: '#818181' }}>Источник: Дизайн-код г. Екатеринбург</span>
          </div>
        </div>
      ) : (<div/>)}
    </div>
  );
}

export default UploadPage;