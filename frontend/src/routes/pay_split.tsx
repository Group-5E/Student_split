import { Card } from '@/components/ui/card'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/pay_split')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className='h-full w-full p-5'>
    <Card className=' flex h-full w-full'>
    </Card>
    </div>
    )
}
