export interface FindItem{
    name:string
    href:string
    pattern:string
}

export interface CheckResponse {
    result:string
    items:FindItem[]
}