import { useEffect, useState } from 'react'
import { primary_dark, site_title } from './Config'

export default function Home() {

  useEffect(() => {
    document.title = site_title
  }, [])
  return (
    <>
    Hello World
    </>
  )
}
