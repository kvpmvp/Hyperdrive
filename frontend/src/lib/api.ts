import axios from 'axios'

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/'
})

export async function listProjects(){
  const { data } = await API.get('/projects')
  return data
}

export async function getProject(id: number){
  const { data } = await API.get(`/projects/${id}`)
  return data
}
