export interface Sentiment{
    skip?:number
    positive?:number
    negative?:number
    neutral?:number
}

export interface FindItem{
    name:string
    href:string
    pattern:string
    rating:number
    ner:string[]
    score:number
    sentiment?:Sentiment
}

export interface CheckResponse {
    result:string
    items:FindItem[]
    sentiment?:Sentiment
    ner:string[]
}